"""List harga per buyer — master data (metadata + baris sheet JSON)."""

from __future__ import annotations

import tempfile
import zipfile
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import BuyerPriceList, BuyerPriceSheetRow
from app.paging import apply_sort, page_dict, parse_page_params
from app.routers.auth import get_current_user, require_roles
from app.schemas import (
    BuyerPriceListCreate,
    BuyerPriceListUpdate,
    BuyerPriceResolveIn,
    BuyerPriceResolveOut,
    BuyerPriceSheetSave,
)
from app.services.buyer_price_import import list_to_api_dict, persist_buyer_folder
from app.services.buyer_price_resolve import resolve_unit_price_for_buyer
from app.services.buyer_registry import ensure_buyer_code

router = APIRouter(tags=["buyer-prices"])


class BuyerPriceSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    buyer_code: str
    currency: str = "USD"
    title: Optional[str] = None
    period_label: Optional[str] = None
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    item_codes: list[str] = Field(default_factory=list)
    filled_price_components: list[str] = Field(default_factory=list)


def _normalize_cell_value(val: Any) -> Any:
    if val is None:
        return ""
    if isinstance(val, (str, int, float, bool)):
        return val
    return str(val)


_NUMERIC_PRICE_KEYS = {
    "COLOR WHITE",
    "COLOR BLACK",
    "COLOR COLOR",
    "FLOURASENT",
    "METALIC",
    "EMBOSS",
    "SPESIAL EMBOSS",
}


def _normalize_price_cell(val: Any) -> Any:
    if val is None:
        return ""
    if isinstance(val, str):
        raw = val.strip()
        if not raw:
            return ""
    else:
        raw = val
    if isinstance(raw, str):
        s = raw.replace(" ", "")
        if "," in s and "." not in s:
            s = s.replace(",", ".")
        elif "," in s and "." in s:
            s = s.replace(",", "")
        raw = s
    try:
        return round(float(raw), 2)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="Kolom harga wajib numerik (COLOR WHITE/COLOR BLACK/COLOR COLOR/FLOURASENT/METALIC/EMBOSS/SPESIAL EMBOSS)",
        )


def _row_to_summary(r: BuyerPriceList) -> BuyerPriceSummaryOut:
    return BuyerPriceSummaryOut(
        id=r.id,
        buyer_code=r.buyer_code,
        currency=r.currency or "USD",
        title=r.title,
        period_label=r.period_label,
        period_start=r.period_start.isoformat() if r.period_start else None,
        period_end=r.period_end.isoformat() if r.period_end else None,
    )


def _extract_sheet_overview(rows: list[BuyerPriceSheetRow]) -> tuple[list[str], list[str]]:
    item_codes: list[str] = []
    filled_components: list[str] = []
    seen_item: set[str] = set()
    seen_component: set[str] = set()
    for row in rows:
        cells = row.cells if isinstance(row.cells, dict) else {}
        item = str(cells.get("ITEM") or "").strip()
        if item and item not in seen_item:
            seen_item.add(item)
            item_codes.append(item)
        for key in _NUMERIC_PRICE_KEYS:
            val = cells.get(key)
            if val in (None, ""):
                continue
            try:
                num = float(val)
            except (TypeError, ValueError):
                continue
            if num <= 0:
                continue
            if key not in seen_component:
                seen_component.add(key)
                filled_components.append(key)
    return item_codes, filled_components


@router.get("/buyer-prices/lists")
def list_buyer_prices(
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=200),
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    sort_by: Optional[str] = Query(None, description="id|buyer_code|title|period_label|currency"),
    sort_dir: Optional[str] = Query(None),
    q: Optional[str] = Query(None, description="Cari buyer_code/title/period"),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    params = parse_page_params(
        page=page,
        page_size=page_size,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_dir=sort_dir or "asc",
        default_page_size=20,
    )
    stmt = select(BuyerPriceList)
    count_stmt = select(func.count(BuyerPriceList.id))
    if q and q.strip():
        like = f"%{q.strip()}%"
        where = (
            BuyerPriceList.buyer_code.ilike(like)
            | BuyerPriceList.title.ilike(like)
            | BuyerPriceList.period_label.ilike(like)
        )
        stmt = stmt.where(where)
        count_stmt = count_stmt.where(where)
    total = int(db.scalar(count_stmt) or 0)
    stmt = apply_sort(
        stmt,
        sortable={
            "id": BuyerPriceList.id,
            "buyer_code": BuyerPriceList.buyer_code,
            "title": BuyerPriceList.title,
            "period_label": BuyerPriceList.period_label,
            "currency": BuyerPriceList.currency,
        },
        sort_by=params.sort_by,
        sort_dir=params.sort_dir,
        default_order=(BuyerPriceList.buyer_code.asc(),),
    )
    rows = list(db.scalars(stmt.limit(params.limit).offset(params.offset)).all())
    if not rows:
        return page_dict(items=[], total=total, params=params)
    list_ids = [r.id for r in rows]
    sheet_rows = db.scalars(
        select(BuyerPriceSheetRow)
        .where(BuyerPriceSheetRow.list_id.in_(list_ids))
        .order_by(BuyerPriceSheetRow.list_id, BuyerPriceSheetRow.row_number)
    ).all()
    grouped: dict[int, list[BuyerPriceSheetRow]] = {x: [] for x in list_ids}
    for sr in sheet_rows:
        grouped.setdefault(sr.list_id, []).append(sr)
    out: list[BuyerPriceSummaryOut] = []
    for r in rows:
        summary = _row_to_summary(r)
        item_codes, filled_components = _extract_sheet_overview(grouped.get(r.id, []))
        summary.item_codes = item_codes
        summary.filled_price_components = filled_components
        out.append(summary)
    return page_dict(items=out, total=total, params=params)


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
    ensure_buyer_code(db, code)
    row = BuyerPriceList(
        buyer_code=code,
        title=body.title,
        period_label=body.period_label,
        period_start=body.period_start,
        period_end=body.period_end,
        currency=body.currency or "USD",
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
            raw_val = raw_cells.get(ck)
            if str(ck).strip().upper() in _NUMERIC_PRICE_KEYS:
                cells[ck] = _normalize_price_cell(raw_val)
            else:
                cells[ck] = _normalize_cell_value(raw_val)
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


@router.post("/buyer-prices/resolve-unit-price", response_model=BuyerPriceResolveOut)
def resolve_unit_price(
    body: BuyerPriceResolveIn,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> BuyerPriceResolveOut:
    """Harga satuan dari sheet list harga buyer (logika pencocokan di server)."""
    r = resolve_unit_price_for_buyer(
        db,
        body.buyer_code,
        material_name=body.material_name,
        color=body.color,
        style_article=body.style_article,
        thickness_text=body.thickness_text,
        color_family=body.color_family,
        emboss=body.emboss,
        factory_code=body.factory_code,
    )
    return BuyerPriceResolveOut(**r)


@router.delete("/buyer-prices/lists/{list_id}")
def delete_buyer_price_list(
    list_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> dict[str, str]:
    row = db.get(BuyerPriceList, list_id)
    if not row:
        raise HTTPException(status_code=404, detail="List harga tidak ditemukan")
    
    # Check if buyer_code is used in PO headers
    from app.models import PoHeader
    related_pos = db.query(PoHeader).filter(PoHeader.buyer == row.buyer_code).count()
    if related_pos > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Buyer {row.buyer_code} tidak bisa dihapus karena masih digunakan di {related_pos} PO"
        )
    
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
