"""List harga per buyer — master data (metadata + baris sheet JSON)."""

from __future__ import annotations

import tempfile
import zipfile
from datetime import date
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Brand, BuyerPriceList, BuyerPriceSheetRow, MasterItem
from app.services.buyer_price_addons import format_required_price_gaps, missing_addons_for_sheet
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
from app.services.buyer_price_period import (
    assert_brand_buyer,
    assert_no_period_overlap,
    assert_period_bounds,
    select_buyer_price_list,
)
from app.services.buyer_price_resolve import resolve_unit_price_for_buyer

router = APIRouter(tags=["buyer-prices"])


class BuyerPriceSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    buyer_code: str
    brand_id: Optional[int] = None
    brand_code: Optional[str] = None
    brand_name: Optional[str] = None
    currency: str = "USD"
    title: Optional[str] = None
    period_label: Optional[str] = None
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    item_codes: list[str] = Field(default_factory=list)
    filled_price_components: list[str] = Field(default_factory=list)
    missing_price_addons: list[str] = Field(default_factory=list)


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


def _row_to_summary(r: BuyerPriceList, brand: Optional[Brand] = None) -> BuyerPriceSummaryOut:
    return BuyerPriceSummaryOut(
        id=r.id,
        buyer_code=r.buyer_code,
        brand_id=r.brand_id,
        brand_code=brand.code if brand else None,
        brand_name=brand.name if brand else None,
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
    stmt = select(BuyerPriceList).outerjoin(Brand, BuyerPriceList.brand_id == Brand.id)
    count_stmt = select(func.count(BuyerPriceList.id)).outerjoin(Brand, BuyerPriceList.brand_id == Brand.id)
    if q and q.strip():
        like = f"%{q.strip()}%"
        where = (
            BuyerPriceList.buyer_code.ilike(like)
            | BuyerPriceList.title.ilike(like)
            | BuyerPriceList.period_label.ilike(like)
            | Brand.name.ilike(like)
            | Brand.code.ilike(like)
        )
        stmt = stmt.where(where)
        count_stmt = count_stmt.where(where)
    total = int(db.scalar(count_stmt) or 0)
    stmt = apply_sort(
        stmt,
        sortable={
            "id": BuyerPriceList.id,
            "buyer_code": BuyerPriceList.buyer_code,
            "brand_name": Brand.name,
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
    brand_ids = [r.brand_id for r in rows if r.brand_id]
    brand_map: dict[int, Brand] = {}
    if brand_ids:
        for brand in db.scalars(select(Brand).where(Brand.id.in_(brand_ids))).all():
            brand_map[int(brand.id)] = brand
    master_items = list(db.scalars(select(MasterItem)).all())
    out: list[BuyerPriceSummaryOut] = []
    for r in rows:
        summary = _row_to_summary(r, brand_map.get(int(r.brand_id)) if r.brand_id else None)
        sheet = grouped.get(r.id, [])
        item_codes, filled_components = _extract_sheet_overview(sheet)
        summary.item_codes = item_codes
        summary.filled_price_components = filled_components
        summary.missing_price_addons = missing_addons_for_sheet(sheet, master_items)
        out.append(summary)
    return page_dict(items=out, total=total, params=params)


@router.post("/buyer-prices/lists", response_model=BuyerPriceSummaryOut)
def create_buyer_price_list(
    body: BuyerPriceListCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing")),
) -> BuyerPriceSummaryOut:
    brand, code = assert_brand_buyer(db, body.brand_id, body.buyer_code)
    assert_period_bounds(body.period_start, body.period_end)
    label = (brand.name or brand.code or code).strip()
    assert_no_period_overlap(
        db,
        brand_id=brand.id,
        buyer_code=code,
        period_start=body.period_start,
        period_end=body.period_end,
        brand_label=label,
    )
    row = BuyerPriceList(
        buyer_code=code,
        brand_id=brand.id,
        title=body.title,
        period_label=body.period_label,
        period_start=body.period_start,
        period_end=body.period_end,
        currency=body.currency or "USD",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _row_to_summary(row, brand)


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
    start = data["period_start"] if "period_start" in data else row.period_start
    end = data["period_end"] if "period_end" in data else row.period_end
    if row.brand_id is not None or start is not None or end is not None:
        assert_period_bounds(start, end)
        brand = db.get(Brand, row.brand_id) if row.brand_id else None
        label = ((brand.name or brand.code) if brand else row.buyer_code) or row.buyer_code
        assert_no_period_overlap(
            db,
            brand_id=row.brand_id,
            buyer_code=row.buyer_code,
            period_start=start,
            period_end=end,
            exclude_id=row.id,
            brand_label=label,
        )
    for key, val in data.items():
        setattr(row, key, val)
    db.commit()
    db.refresh(row)
    brand = db.get(Brand, row.brand_id) if row.brand_id else None
    return _row_to_summary(row, brand)


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

    master_items = list(db.scalars(select(MasterItem)).all())
    gaps = format_required_price_gaps(body.rows, master_items)
    if gaps:
        raise HTTPException(status_code=400, detail=gaps)

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
    as_of: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> dict[str, Any]:
    row = select_buyer_price_list(db, buyer_code, as_of)
    if not row:
        raise HTTPException(status_code=404, detail="List harga untuk buyer dan tanggal ini tidak ditemukan")
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
        as_of=body.as_of,
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
