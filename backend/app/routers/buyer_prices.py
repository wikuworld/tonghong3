"""List harga per buyer — master data (metadata + baris sheet JSON)."""

from __future__ import annotations

import tempfile
import zipfile
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, ConfigDict
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import BuyerPriceList, BuyerPriceSheetRow
from app.routers.auth import get_current_user, require_roles
from app.schemas import BuyerPriceListCreate, BuyerPriceListUpdate, BuyerPriceSheetSave
from app.services.buyer_price_import import list_to_api_dict, persist_buyer_folder

router = APIRouter(tags=["buyer-prices"])


class BuyerPriceSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    buyer_code: str
    title: Optional[str] = None
    period_label: Optional[str] = None
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    source_label: Optional[str] = None


def _normalize_cell_value(val: Any) -> Any:
    if val is None:
        return ""
    if isinstance(val, (str, int, float, bool)):
        return val
    return str(val)


def _row_to_summary(r: BuyerPriceList) -> BuyerPriceSummaryOut:
    return BuyerPriceSummaryOut(
        id=r.id,
        buyer_code=r.buyer_code,
        title=r.title,
        period_label=r.period_label,
        period_start=r.period_start.isoformat() if r.period_start else None,
        period_end=r.period_end.isoformat() if r.period_end else None,
        source_label=r.source_label,
    )


@router.get("/buyer-prices/lists", response_model=list[BuyerPriceSummaryOut])
def list_buyer_prices(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> list[BuyerPriceSummaryOut]:
    rows = db.scalars(select(BuyerPriceList).order_by(BuyerPriceList.buyer_code)).all()
    return [_row_to_summary(r) for r in rows]


@router.post("/buyer-prices/lists", response_model=BuyerPriceSummaryOut)
def create_buyer_price_list(
    body: BuyerPriceListCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing")),
) -> BuyerPriceSummaryOut:
    code = body.buyer_code.strip().upper()
    if not code:
        raise HTTPException(status_code=400, detail="Kode buyer wajib diisi")
    existing = db.scalars(select(BuyerPriceList).where(BuyerPriceList.buyer_code == code)).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"List untuk buyer {code} sudah ada")
    row = BuyerPriceList(
        buyer_code=code,
        title=body.title,
        period_label=body.period_label,
        period_start=body.period_start,
        period_end=body.period_end,
        source_label=body.source_label,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _row_to_summary(row)


@router.put("/buyer-prices/lists/{list_id}", response_model=BuyerPriceSummaryOut)
def update_buyer_price_list(
    list_id: int,
    body: BuyerPriceListUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing")),
) -> BuyerPriceSummaryOut:
    row = db.get(BuyerPriceList, list_id)
    if not row:
        raise HTTPException(status_code=404, detail="List harga tidak ditemukan")
    data = body.model_dump(exclude_unset=True)
    for key, val in data.items():
        setattr(row, key, val)
    db.commit()
    db.refresh(row)
    return _row_to_summary(row)


@router.get("/buyer-prices/lists/{list_id}")
def get_buyer_price_list(
    list_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> dict[str, Any]:
    data = list_to_api_dict(db, list_id)
    if not data:
        raise HTTPException(status_code=404, detail="List harga tidak ditemukan")
    return data


@router.put("/buyer-prices/lists/{list_id}/sheet")
def save_buyer_price_sheet(
    list_id: int,
    body: BuyerPriceSheetSave,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing")),
) -> dict[str, Any]:
    """Ganti seluruh baris sheet + simpan urutan kolom di `meta_json.column_keys`."""
    lst = db.get(BuyerPriceList, list_id)
    if not lst:
        raise HTTPException(status_code=404, detail="List harga tidak ditemukan")

    seen: set[str] = set()
    column_keys: list[str] = []
    for raw in body.column_keys:
        k = (raw or "").strip()
        if not k or k in seen:
            continue
        seen.add(k)
        column_keys.append(k)

    meta = dict(lst.meta_json or {})
    meta["column_keys"] = column_keys
    lst.meta_json = meta

    db.execute(delete(BuyerPriceSheetRow).where(BuyerPriceSheetRow.list_id == list_id))

    for i, raw_cells in enumerate(body.rows):
        if not isinstance(raw_cells, dict):
            raw_cells = {}
        cells: dict[str, Any] = {}
        for ck in column_keys:
            cells[ck] = _normalize_cell_value(raw_cells.get(ck))
        db.add(BuyerPriceSheetRow(list_id=list_id, row_number=i, cells=cells))

    db.commit()
    data = list_to_api_dict(db, list_id)
    if not data:
        raise HTTPException(status_code=404, detail="List harga tidak ditemukan")
    return data


@router.get("/buyer-prices/by-buyer/{buyer_code}")
def get_by_buyer(
    buyer_code: str,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> dict[str, Any]:
    row = db.scalars(
        select(BuyerPriceList).where(BuyerPriceList.buyer_code == buyer_code.upper())
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Buyer tidak ditemukan")
    return list_to_api_dict(db, row.id)


@router.delete("/buyer-prices/lists/{list_id}")
def delete_buyer_price_list(
    list_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> dict[str, str]:
    row = db.get(BuyerPriceList, list_id)
    if not row:
        raise HTTPException(status_code=404, detail="List harga tidak ditemukan")
    db.delete(row)
    db.commit()
    return {"status": "deleted"}


@router.post("/buyer-prices/import-upload")
async def import_upload(
    db: Session = Depends(get_db),
    files: list[UploadFile] = File(...),
    source_label: Optional[str] = Form(None),
    _user=Depends(require_roles("admin", "marketing")),
) -> list[dict[str, Any]]:
    if not files:
        raise HTTPException(status_code=400, detail="Tidak ada file")
    with tempfile.TemporaryDirectory() as tmp:
        tpath = Path(tmp)
        for uf in files:
            dest = tpath / (uf.filename or "unknown.csv")
            dest.write_bytes(await uf.read())
        try:
            lst = persist_buyer_folder(db, tpath, source_label)
            db.commit()
        except ValueError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e)) from e
    return [list_to_api_dict(db, x.id) for x in lst]


@router.post("/buyer-prices/import-zip")
async def import_zip(
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    source_label: Optional[str] = Form(None),
    _user=Depends(require_roles("admin", "marketing")),
) -> list[dict[str, Any]]:
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="File kosong")
    with tempfile.TemporaryDirectory() as tmp:
        tpath = Path(tmp)
        zpath = tpath / "u.zip"
        zpath.write_bytes(raw)
        try:
            with zipfile.ZipFile(zpath) as zf:
                zf.extractall(tpath)
        except zipfile.BadZipFile as e:
            raise HTTPException(status_code=400, detail="Bukan ZIP valid") from e
        try:
            lst = persist_buyer_folder(db, tpath, source_label)
            db.commit()
        except ValueError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e)) from e
    return [list_to_api_dict(db, x.id) for x in lst]
