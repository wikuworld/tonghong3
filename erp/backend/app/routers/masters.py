"""Master: Brand & Customer PIC (CR §3.1)."""

from __future__ import annotations

import csv
import io
import logging
import zipfile
from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

logger = logging.getLogger(__name__)
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field
from app.schemas import (
    MasterItemCreate,
    MasterItemDimensionValuesOut,
    MasterItemNextCodeOut,
    MasterItemOut,
    MasterItemPageOut,
    MasterItemResolveByDimensionsOut,
    MasterItemStatsOut,
    MasterItemSwatchCascadeOut,
    MasterItemSwatchEmbossOut,
    MasterPriceOut,
)
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.timeutil import app_now
from app.models import (
    BrandBuyerMap,
    Brand,
    BuyerPriceList,
    ColorSwatchRecipe,
    CsiColorMaster,
    Customer,
    CustomerBrandMapping,
    CustomerPic,
    FluorescentColorMaster,
    MasterItem,
    MasterPrice,
)
from app.routers.auth import get_current_user, require_roles
from app.services.fluorescent_color import (
    VALID_COLOR_CLASSES,
    apply_fluorescent_fields,
    find_existing,
    gather_bundled_rows,
    parse_fluorescent_upload,
    upsert_fluorescent_rows,
)
from app.services.color_code import apply_item_color_extract
from app.services.master_items_excel import (
    export_master_items_template_xlsx,
    export_master_items_xlsx,
    import_master_items_xlsx,
)
from app.services.color_swatch import UnknownBuyerRejectError
from app.services.master_item_code import (
    allocate_next_item_code,
    list_swatch_colors,
    list_swatch_embosses,
    list_swatch_materials,
)
from app.services.master_item_dimensions import (
    distinct_colors,
    distinct_embosses,
    distinct_item_codes,
    distinct_material_names,
    distinct_thicknesses,
    filter_by_category,
    resolve_by_dimensions,
)

router = APIRouter(tags=["masters"])


class BrandIn(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: Optional[str] = None
    customer_ids: list[int] = []


class BrandOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: Optional[str] = None
    name: Optional[str] = None
    customer_id: Optional[int] = None
    customer_ids: list[int] = []
    buyer_codes: list[str] = []


class BrandBuyerMapIn(BaseModel):
    model_config = ConfigDict(extra="ignore")

    buyer_codes: list[str] = []


class BrandBuyerMapOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    brand_id: int
    buyer_code: str


class PicIn(BaseModel):
    model_config = ConfigDict(extra="ignore")

    customer_id: Optional[int] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    title: Optional[str] = None


class PicOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: Optional[int] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    title: Optional[str] = None


class FluorescentColorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    buyer_code: str
    brand_id: Optional[int] = None
    season_label: Optional[str] = None
    season_year: Optional[int] = None
    season_type: Optional[str] = None
    color_name: str
    color_code: Optional[str] = None
    color_class: str
    source_file: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


_FLUORESCENT_SORTABLE = {
    "created_at": FluorescentColorMaster.created_at,
    "updated_at": FluorescentColorMaster.updated_at,
    "buyer_code": FluorescentColorMaster.buyer_code,
    "season_label": FluorescentColorMaster.season_label,
    "season_year": FluorescentColorMaster.season_year,
    "color_name": FluorescentColorMaster.color_name,
    "color_code": FluorescentColorMaster.color_code,
    "color_class": FluorescentColorMaster.color_class,
}


class FluorescentColorPageOut(BaseModel):
    items: list[FluorescentColorOut]
    total: int
    limit: int
    offset: int


class FluorescentColorFormOptionsOut(BaseModel):
    buyer_codes: list[str] = Field(default_factory=list)
    color_classes: list[str] = Field(default_factory=list)
    season_labels: list[str] = Field(default_factory=list)
    season_labels_by_buyer: dict[str, list[str]] = Field(default_factory=dict)
    season_years: list[int] = Field(default_factory=list)
    season_types: list[str] = Field(default_factory=list)
    color_names_by_buyer: dict[str, list[str]] = Field(default_factory=dict)
    color_codes_by_buyer: dict[str, list[str]] = Field(default_factory=dict)
    color_names_by_buyer_season: dict[str, dict[str, list[str]]] = Field(default_factory=dict)


class FluorescentColorIn(BaseModel):
    model_config = ConfigDict(extra="ignore")

    buyer_code: str = Field(..., min_length=1, max_length=32)
    season_label: Optional[str] = Field(default=None, max_length=64)
    season_year: Optional[int] = None
    season_type: Optional[str] = Field(default=None, max_length=16)
    color_name: str = Field(..., min_length=1, max_length=255)
    color_code: Optional[str] = Field(default=None, max_length=64)
    color_class: str = Field(default="fluorescent", max_length=32)
    source_file: Optional[str] = Field(default=None, max_length=255)
    is_active: bool = True


class FluorescentImportResultOut(BaseModel):
    inserted: int
    updated: int
    total: int
    warnings: list[str] = Field(default_factory=list)


def _buyer_codes_by_brand(db: Session, brand_ids: list[int]) -> dict[int, list[str]]:
    if not brand_ids:
        return {}
    rows = db.scalars(
        select(BrandBuyerMap).where(BrandBuyerMap.brand_id.in_(brand_ids))
    ).all()
    grouped: dict[int, list[str]] = {}
    for row in rows:
        if not row.buyer_code:
            continue
        grouped.setdefault(int(row.brand_id), []).append(str(row.buyer_code))
    for codes in grouped.values():
        codes.sort()
    return grouped


def _brand_out(brand: Brand, buyers_by_brand: dict[int, list[str]]) -> BrandOut:
    mapped_ids = sorted(
        {int(m.customer_id) for m in (brand.customer_mappings or []) if m.customer_id is not None}
    )
    return BrandOut(
        id=brand.id,
        code=brand.code,
        name=brand.name,
        customer_id=mapped_ids[0] if mapped_ids else None,
        customer_ids=mapped_ids,
        buyer_codes=list(buyers_by_brand.get(int(brand.id), [])),
    )


@router.get("/masters/brands", response_model=list[BrandOut])
def list_brands(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> list[BrandOut]:
    brands = list(db.scalars(select(Brand).order_by(Brand.id.desc())).all())
    buyers_by_brand = _buyer_codes_by_brand(db, [int(b.id) for b in brands])
    return [_brand_out(brand, buyers_by_brand) for brand in brands]


@router.get("/masters/brands/page")
def list_brands_page(
    q: Optional[str] = Query(None, description="Cari kode/nama brand"),
    customer_id: Optional[int] = Query(None),
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=200),
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    sort_by: Optional[str] = Query(None, description="id|code|name"),
    sort_dir: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    from app.paging import apply_sort, page_dict, parse_page_params
    from app.models import CustomerBrandMapping

    params = parse_page_params(
        page=page,
        page_size=page_size,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_dir=sort_dir or "desc",
    )
    stmt = select(Brand)
    count_stmt = select(func.count(Brand.id))
    if q and q.strip():
        like = f"%{q.strip()}%"
        where = or_(Brand.code.ilike(like), Brand.name.ilike(like))
        stmt = stmt.where(where)
        count_stmt = count_stmt.where(where)
    if customer_id:
        stmt = stmt.where(
            Brand.id.in_(
                select(CustomerBrandMapping.brand_id).where(
                    CustomerBrandMapping.customer_id == customer_id
                )
            )
        )
        count_stmt = count_stmt.where(
            Brand.id.in_(
                select(CustomerBrandMapping.brand_id).where(
                    CustomerBrandMapping.customer_id == customer_id
                )
            )
        )
    total = int(db.scalar(count_stmt) or 0)
    stmt = apply_sort(
        stmt,
        sortable={"id": Brand.id, "code": Brand.code, "name": Brand.name},
        sort_by=params.sort_by,
        sort_dir=params.sort_dir,
        default_order=(Brand.id.desc(),),
    )
    brands = list(db.scalars(stmt.limit(params.limit).offset(params.offset)).all())
    buyers_by_brand = _buyer_codes_by_brand(db, [int(b.id) for b in brands])
    out = [_brand_out(brand, buyers_by_brand) for brand in brands]
    return page_dict(items=out, total=total, params=params)


@router.post("/masters/brands", response_model=BrandOut)
def create_brand(
    body: BrandIn,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> Brand:
    brand_name = (body.name or "").strip()
    if not brand_name:
        raise HTTPException(status_code=400, detail="Nama brand wajib diisi")
    dup = db.scalars(select(Brand).where(Brand.code == brand_name)).first()
    if dup:
        raise HTTPException(
            status_code=400,
            detail=f"Kode brand '{brand_name}' sudah dipakai (harus unik)",
        )
    row = Brand(name=brand_name, code=brand_name)
    db.add(row)
    db.flush()
    customer_ids = sorted({int(x) for x in (body.customer_ids or []) if x is not None})
    for customer_id in customer_ids:
        customer = db.get(Customer, customer_id)
        if customer:
            db.add(CustomerBrandMapping(customer_id=customer_id, brand_id=row.id, is_default=False))
    db.commit()
    db.refresh(row)
    return _brand_out(row, _buyer_codes_by_brand(db, [int(row.id)]))


@router.put("/masters/brands/{brand_id}", response_model=BrandOut)
def update_brand(
    brand_id: int,
    body: BrandIn,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> Brand:
    row = db.get(Brand, brand_id)
    if not row:
        raise HTTPException(status_code=404, detail="Brand tidak ada")
    data = body.model_dump(exclude_unset=True)
    if "name" in data:
        brand_name = (data.get("name") or "").strip()
        if not brand_name:
            raise HTTPException(status_code=400, detail="Nama brand wajib diisi")
        other = db.scalars(
            select(Brand).where(Brand.code == brand_name, Brand.id != brand_id)
        ).first()
        if other:
            raise HTTPException(
                status_code=400,
                detail=f"Kode brand '{brand_name}' sudah dipakai (harus unik)",
            )
        row.name = brand_name
        # Tetap sinkronkan code dari nama agar modul lama tidak putus.
        row.code = brand_name
        row.updated_at = app_now()
    if "customer_ids" in data:
        customer_ids = sorted({int(x) for x in (data.get("customer_ids") or []) if x is not None})
        db.query(CustomerBrandMapping).filter(CustomerBrandMapping.brand_id == brand_id).delete()
        for customer_id in customer_ids:
            customer = db.get(Customer, customer_id)
            if customer:
                db.add(CustomerBrandMapping(customer_id=customer_id, brand_id=brand_id, is_default=False))
    db.commit()
    db.refresh(row)
    return _brand_out(row, _buyer_codes_by_brand(db, [int(row.id)]))


@router.delete("/masters/brands/{brand_id}")
def delete_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> dict[str, str]:
    row = db.get(Brand, brand_id)
    if not row:
        raise HTTPException(status_code=404, detail="Brand tidak ada")
    
    from app.models import PoHeader, CustomerBrandMapping
    
    errors = []
    
    related_pos = db.query(PoHeader).filter(PoHeader.brand_id == brand_id).count()
    if related_pos > 0:
        errors.append(f"{related_pos} PO")
    
    related_mappings = db.query(CustomerBrandMapping).filter(CustomerBrandMapping.brand_id == brand_id).count()
    if related_mappings > 0:
        errors.append(f"{related_mappings} Customer Brand Mapping")
    
    if errors:
        raise HTTPException(
            status_code=400, 
            detail=f"Brand tidak bisa dihapus karena masih digunakan di: {', '.join(errors)}"
        )
    
    db.delete(row)
    db.commit()
    return {"status": "deleted"}


@router.post("/masters/brands/seed-from-buyers")
def seed_brands_from_buyers(
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> dict[str, int]:
    from app.services.buyer_registry import ensure_buyer_code

    buyer_codes = db.scalars(select(BuyerPriceList.buyer_code)).all()
    created = 0
    mapped = 0
    for code in sorted({str(x).strip() for x in buyer_codes if str(x).strip()}):
        ensure_buyer_code(db, code)
        brand = db.scalars(select(Brand).where(Brand.code == code)).first()
        if not brand:
            brand = Brand(code=code, name=code)
            db.add(brand)
            db.flush()
            created += 1
        existing_map = db.scalars(
            select(BrandBuyerMap).where(
                BrandBuyerMap.brand_id == brand.id,
                BrandBuyerMap.buyer_code == code,
            )
        ).first()
        if not existing_map:
            db.add(BrandBuyerMap(brand_id=brand.id, buyer_code=code))
            mapped += 1
    db.commit()
    return {"created": created, "mapped": mapped}


@router.get("/masters/brands/{brand_id}/buyers", response_model=list[BrandBuyerMapOut])
def list_brand_buyers(
    brand_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> list[BrandBuyerMap]:
    if not db.get(Brand, brand_id):
        raise HTTPException(status_code=404, detail="Brand tidak ada")
    rows = db.scalars(
        select(BrandBuyerMap)
        .where(BrandBuyerMap.brand_id == brand_id)
        .order_by(BrandBuyerMap.buyer_code.asc())
    ).all()
    return list(rows)


@router.put("/masters/brands/{brand_id}/buyers", response_model=list[BrandBuyerMapOut])
def replace_brand_buyers(
    brand_id: int,
    body: BrandBuyerMapIn,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> list[BrandBuyerMap]:
    if not db.get(Brand, brand_id):
        raise HTTPException(status_code=404, detail="Brand tidak ada")
    from app.services.buyer_registry import ensure_buyer_code

    db.query(BrandBuyerMap).filter(BrandBuyerMap.brand_id == brand_id).delete()
    cleaned = sorted({str(code).strip().upper() for code in body.buyer_codes if str(code).strip()})
    for code in cleaned:
        ensure_buyer_code(db, code)
        db.add(BrandBuyerMap(brand_id=brand_id, buyer_code=code))
    db.commit()
    rows = db.scalars(
        select(BrandBuyerMap)
        .where(BrandBuyerMap.brand_id == brand_id)
        .order_by(BrandBuyerMap.buyer_code.asc())
    ).all()
    return list(rows)


@router.get("/masters/fluorescent-colors", response_model=list[FluorescentColorOut])
def list_fluorescent_colors(
    buyer_code: Optional[str] = None,
    season_label: Optional[str] = None,
    color_class: Optional[str] = None,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> list[FluorescentColorMaster]:
    stmt = select(FluorescentColorMaster).where(FluorescentColorMaster.is_active.is_(True))
    if buyer_code:
        b = buyer_code.strip().upper()
        stmt = stmt.where(FluorescentColorMaster.buyer_code.in_([b, "GLOBAL"]))
    if season_label:
        stmt = stmt.where(FluorescentColorMaster.season_label == season_label.strip())
    if color_class:
        stmt = stmt.where(FluorescentColorMaster.color_class == color_class.strip().lower())
    rows = db.scalars(
        stmt.order_by(
            FluorescentColorMaster.buyer_code.asc(),
            FluorescentColorMaster.season_year.desc(),
            FluorescentColorMaster.color_name.asc(),
        )
    ).all()
    return list(rows)


@router.get("/masters/fluorescent-colors/page", response_model=FluorescentColorPageOut)
def list_fluorescent_colors_page(
    buyer_code: Optional[str] = None,
    season_label: Optional[str] = None,
    color_class: Optional[str] = None,
    q: Optional[str] = Query(None, description="Search color code/name/season"),
    sort_by: Optional[str] = Query(
        None,
        description="Kolom sort: created_at, updated_at, buyer_code, season_label, season_year, color_name, color_code, color_class",
    ),
    sort_dir: str = Query("asc", description="asc atau desc"),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> FluorescentColorPageOut:
    stmt = select(FluorescentColorMaster).where(FluorescentColorMaster.is_active.is_(True))
    count_stmt = select(func.count(FluorescentColorMaster.id)).where(FluorescentColorMaster.is_active.is_(True))
    if buyer_code:
        b = buyer_code.strip().upper()
        stmt = stmt.where(FluorescentColorMaster.buyer_code.in_([b, "GLOBAL"]))
        count_stmt = count_stmt.where(FluorescentColorMaster.buyer_code.in_([b, "GLOBAL"]))
    if season_label:
        stmt = stmt.where(FluorescentColorMaster.season_label == season_label.strip())
        count_stmt = count_stmt.where(FluorescentColorMaster.season_label == season_label.strip())
    if color_class:
        c = color_class.strip().lower()
        stmt = stmt.where(FluorescentColorMaster.color_class == c)
        count_stmt = count_stmt.where(FluorescentColorMaster.color_class == c)
    if q:
        like = f"%{q.strip()}%"
        where_clause = or_(
            FluorescentColorMaster.color_name.ilike(like),
            FluorescentColorMaster.color_code.ilike(like),
            FluorescentColorMaster.season_label.ilike(like),
            FluorescentColorMaster.buyer_code.ilike(like),
        )
        stmt = stmt.where(where_clause)
        count_stmt = count_stmt.where(where_clause)
    total = int(db.scalar(count_stmt) or 0)

    sort_key = (sort_by or "").strip().lower()
    col = _FLUORESCENT_SORTABLE.get(sort_key)
    if col is not None:
        descending = sort_dir.strip().lower() == "desc"
        primary = col.desc() if descending else col.asc()
        order_clauses = (primary, FluorescentColorMaster.id.asc())
    else:
        order_clauses = (
            FluorescentColorMaster.buyer_code.asc(),
            FluorescentColorMaster.season_year.desc(),
            FluorescentColorMaster.color_name.asc(),
        )

    items = list(
        db.scalars(stmt.order_by(*order_clauses).limit(limit).offset(offset)).all()
    )
    return FluorescentColorPageOut(items=items, total=total, limit=limit, offset=offset)


@router.get("/masters/fluorescent-colors/form-options", response_model=FluorescentColorFormOptionsOut)
def fluorescent_color_form_options(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> FluorescentColorFormOptionsOut:
    """Opsi dropdown form tambah/edit fluorescent — dari registry buyer & data existing."""
    from app.services.buyer_registry import list_active_buyer_codes

    rows = list(
        db.scalars(
            select(FluorescentColorMaster).where(FluorescentColorMaster.is_active.is_(True))
        ).all()
    )
    buyer_codes: set[str] = set(list_active_buyer_codes(db))

    season_labels: set[str] = set()
    season_labels_by_buyer: dict[str, set[str]] = {}
    season_years: set[int] = set()
    season_types: set[str] = set()
    color_names_by_buyer: dict[str, set[str]] = {}
    color_codes_by_buyer: dict[str, set[str]] = {}
    color_names_by_buyer_season: dict[str, dict[str, set[str]]] = {}

    for row in rows:
        buyer = (row.buyer_code or "GLOBAL").strip().upper()
        buyer_codes.add(buyer)
        season = (row.season_label or "").strip()
        if season:
            season_labels.add(season)
            season_labels_by_buyer.setdefault(buyer, set()).add(season)
        if row.season_year is not None:
            season_years.add(int(row.season_year))
        st = (row.season_type or "").strip().upper()
        if st:
            season_types.add(st)
        if row.color_name:
            color_names_by_buyer.setdefault(buyer, set()).add(row.color_name.strip())
            if season:
                color_names_by_buyer_season.setdefault(buyer, {}).setdefault(season, set()).add(
                    row.color_name.strip()
                )
        if row.color_code:
            color_codes_by_buyer.setdefault(buyer, set()).add(row.color_code.strip())

    return FluorescentColorFormOptionsOut(
        buyer_codes=sorted(buyer_codes),
        color_classes=sorted(VALID_COLOR_CLASSES),
        season_labels=sorted(season_labels),
        season_labels_by_buyer={k: sorted(v) for k, v in sorted(season_labels_by_buyer.items())},
        season_years=sorted(season_years, reverse=True),
        season_types=sorted(season_types),
        color_names_by_buyer={k: sorted(v) for k, v in sorted(color_names_by_buyer.items())},
        color_codes_by_buyer={k: sorted(v) for k, v in sorted(color_codes_by_buyer.items())},
        color_names_by_buyer_season={
            buyer: {season: sorted(names) for season, names in sorted(seasons.items())}
            for buyer, seasons in sorted(color_names_by_buyer_season.items())
        },
    )


@router.get("/masters/fluorescent-colors/{row_id}", response_model=FluorescentColorOut)
def get_fluorescent_color(
    row_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> FluorescentColorMaster:
    row = db.get(FluorescentColorMaster, row_id)
    if not row or not row.is_active:
        raise HTTPException(status_code=404, detail="Master fluorescent tidak ditemukan")
    return row


@router.post("/masters/fluorescent-colors", response_model=FluorescentColorOut)
def create_fluorescent_color(
    body: FluorescentColorIn,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing")),
) -> FluorescentColorMaster:
    data = apply_fluorescent_fields(body.model_dump())
    if not data["color_name"]:
        raise HTTPException(status_code=400, detail="Nama warna wajib diisi")
    dup = find_existing(
        db,
        buyer_code=data["buyer_code"],
        season_label=data["season_label"],
        color_code=data["color_code"],
        color_name=data["color_name"],
    )
    if dup:
        raise HTTPException(status_code=400, detail="Kombinasi buyer/season/kode/nama sudah ada")
    from app.services.buyer_registry import ensure_buyer_code

    buyer = data["buyer_code"]
    ensure_buyer_code(db, buyer)
    if buyer and buyer != "GLOBAL":
        brand = db.scalars(select(Brand).where(Brand.code == buyer)).first()
        data["brand_id"] = brand.id if brand else None
    else:
        data["brand_id"] = None
    row = FluorescentColorMaster(**data)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/masters/fluorescent-colors/{row_id}", response_model=FluorescentColorOut)
def update_fluorescent_color(
    row_id: int,
    body: FluorescentColorIn,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing")),
) -> FluorescentColorMaster:
    row = db.get(FluorescentColorMaster, row_id)
    if not row:
        raise HTTPException(status_code=404, detail="Master fluorescent tidak ditemukan")
    data = apply_fluorescent_fields(body.model_dump())
    dup = find_existing(
        db,
        buyer_code=data["buyer_code"],
        season_label=data["season_label"],
        color_code=data["color_code"],
        color_name=data["color_name"],
        exclude_id=row_id,
    )
    if dup:
        raise HTTPException(status_code=400, detail="Kombinasi buyer/season/kode/nama bentrok")
    from app.services.buyer_registry import ensure_buyer_code

    for key, val in data.items():
        setattr(row, key, val)
    buyer = data["buyer_code"]
    ensure_buyer_code(db, buyer)
    if buyer and buyer != "GLOBAL":
        brand = db.scalars(select(Brand).where(Brand.code == buyer)).first()
        row.brand_id = brand.id if brand else None
    else:
        row.brand_id = None
    row.updated_at = app_now()
    db.commit()
    db.refresh(row)
    return row


@router.delete("/masters/fluorescent-colors/{row_id}")
def delete_fluorescent_color(
    row_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> dict[str, str]:
    row = db.get(FluorescentColorMaster, row_id)
    if not row:
        raise HTTPException(status_code=404, detail="Master fluorescent tidak ditemukan")
    row.is_active = False
    row.updated_at = app_now()
    db.commit()
    return {"status": "deactivated"}


@router.post("/masters/fluorescent-colors/import-bundled", response_model=FluorescentImportResultOut)
def import_fluorescent_bundled(
    reject_unknown_buyer: bool = Query(
        False,
        description="Tolak import (400) jika ada buyer_code di luar registry",
    ),
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> FluorescentImportResultOut:
    """Upsert dari CSV dokumentasi (NB, ADIDAS, GLOBAL, UA)."""
    try:
        rows = gather_bundled_rows()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if not rows:
        raise HTTPException(status_code=400, detail="Tidak ada baris valid")
    try:
        stats = upsert_fluorescent_rows(
            db, rows, reject_unknown_buyer=reject_unknown_buyer
        )
    except UnknownBuyerRejectError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return FluorescentImportResultOut(**stats)


@router.post("/masters/fluorescent-colors/import-csv", response_model=FluorescentImportResultOut)
async def import_fluorescent_csv(
    file: UploadFile = File(...),
    reject_unknown_buyer: bool = Query(
        False,
        description="Tolak import (400) jika ada buyer_code di luar registry",
    ),
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing")),
) -> FluorescentImportResultOut:
    """Upload CSV fluorescent (format NB/ADIDAS/GLOBAL/UA atau kolom generic)."""
    raw = await file.read()
    filename = file.filename or "upload.csv"
    rows = parse_fluorescent_upload(raw, filename)
    if not rows:
        raise HTTPException(status_code=400, detail="Tidak ada baris valid dalam file CSV")
    try:
        stats = upsert_fluorescent_rows(
            db, rows, reject_unknown_buyer=reject_unknown_buyer
        )
    except UnknownBuyerRejectError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return FluorescentImportResultOut(**stats)


@router.get("/masters/customer-pics", response_model=list[PicOut])
def list_pics(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> list[CustomerPic]:
    return list(db.scalars(select(CustomerPic).order_by(CustomerPic.id.desc())).all())


@router.post("/masters/customer-pics", response_model=PicOut)
def create_pic(
    body: PicIn,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> CustomerPic:
    row = CustomerPic(**body.model_dump(exclude_unset=True))
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/masters/customer-pics/{pic_id}")
def delete_pic(
    pic_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> dict[str, str]:
    row = db.get(CustomerPic, pic_id)
    if not row:
        raise HTTPException(status_code=404, detail="PIC tidak ada")
    db.delete(row)
    db.commit()
    return {"status": "deleted"}


# --- Master Item (FG / sheet Master Item) ---
def _annotate_item_color_links(db: Session, items: list[MasterItemOut]) -> list[MasterItemOut]:
    codes = {(i.color_code or "").strip().upper() for i in items if i.color_code}
    codes.discard("")
    if not codes:
        return items
    csi_codes = {
        str(c).strip().upper()
        for c in db.scalars(
            select(CsiColorMaster.color_code).where(
                CsiColorMaster.is_active.is_(True),
                CsiColorMaster.color_code.in_(codes),
            )
        ).all()
    }
    sw_codes = {
        str(c).strip().upper()
        for c in db.scalars(
            select(ColorSwatchRecipe.color_code).where(
                ColorSwatchRecipe.is_active.is_(True),
                ColorSwatchRecipe.color_code.in_(codes),
            )
        ).all()
    }
    for item in items:
        code = (item.color_code or "").strip().upper()
        item.in_csi = bool(code and code in csi_codes)
        item.in_swatch = bool(code and code in sw_codes)
    return items


def _master_item_suede_count(counts: dict[str, int]) -> int:
    return int(counts.get("Suede", 0)) + int(counts.get("Suide", 0))


def _master_item_stats(db: Session) -> MasterItemStatsOut:
    rows = db.execute(
        select(MasterItem.category, func.count()).group_by(MasterItem.category)
    ).all()
    counts = {str(cat or ""): int(n) for cat, n in rows}
    pu = counts.get("PU", 0)
    suide = _master_item_suede_count(counts)
    subkon = counts.get("SubKon", 0)
    known = {"PU", "Suede", "Suide", "SubKon"}
    return MasterItemStatsOut(
        total=pu + suide + subkon + sum(v for k, v in counts.items() if k not in known),
        pu=pu,
        suide=suide,
        subkon=subkon,
    )


def _apply_master_item_list_filters(
    stmt,
    *,
    keyword: Optional[str],
    category: Optional[str],
):
    if category and str(category).strip():
        cat = str(category).strip()
        if cat.lower() in ("suede", "suide"):
            stmt = stmt.where(func.lower(MasterItem.category).in_(("suede", "suide")))
        else:
            stmt = stmt.where(MasterItem.category == cat)
    if keyword and str(keyword).strip():
        like = f"%{str(keyword).strip()}%"
        stmt = stmt.where(
            or_(
                MasterItem.item_code.ilike(like),
                MasterItem.category.ilike(like),
                MasterItem.material_name.ilike(like),
                MasterItem.thickness_range.ilike(like),
                MasterItem.color.ilike(like),
                MasterItem.emboss.ilike(like),
            )
        )
    return stmt


@router.get("/masters/items", response_model=list[MasterItemOut])
def list_master_items(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> list[MasterItem]:
    return list(db.scalars(select(MasterItem).order_by(MasterItem.item_code)).all())


@router.get("/masters/items/page", response_model=MasterItemPageOut)
def list_master_items_page(
    keyword: Optional[str] = Query(None, description="Cari kode, material, warna, emboss"),
    category: Optional[str] = Query(None, description="Filter kategori: PU | Suede | SubKon"),
    sort_by: Optional[str] = Query(
        None,
        description="Kolom sort: item_code, category, material_name, thickness, color, emboss, id",
    ),
    sort_dir: str = Query("asc", description="asc atau desc"),
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=200),
    limit: Optional[int] = Query(None, ge=1, le=200),
    offset: Optional[int] = Query(None, ge=0),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> MasterItemPageOut:
    from app.paging import apply_sort, parse_page_params

    params = parse_page_params(
        page=page,
        page_size=page_size,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_dir=sort_dir or "asc",
        default_page_size=50,
    )
    base = select(MasterItem)
    count_stmt = select(func.count(MasterItem.id))
    base = _apply_master_item_list_filters(base, keyword=keyword, category=category)
    count_stmt = _apply_master_item_list_filters(count_stmt, keyword=keyword, category=category)
    total = int(db.scalar(count_stmt) or 0)
    sortable = {
        "item_code": MasterItem.item_code,
        "category": MasterItem.category,
        "material_name": MasterItem.material_name,
        "thickness": MasterItem.thickness_range,
        "thickness_range": MasterItem.thickness_range,
        "color": MasterItem.color,
        "emboss": MasterItem.emboss,
        "id": MasterItem.id,
    }
    base = apply_sort(
        base,
        sortable=sortable,
        sort_by=params.sort_by,
        sort_dir=params.sort_dir,
        default_order=(MasterItem.item_code.asc(), MasterItem.id.asc()),
    )
    items = list(
        db.scalars(base.limit(params.limit).offset(params.offset)).all()
    )
    out_items = _annotate_item_color_links(
        db, [MasterItemOut.model_validate(i) for i in items]
    )
    return MasterItemPageOut(
        items=out_items,
        total=total,
        limit=params.limit,
        offset=params.offset,
        page=params.page,
        page_size=params.page_size,
        stats=_master_item_stats(db),
    )


def _filter_master_items_by_category(
    rows: list[MasterItem],
    category: Optional[str],
) -> list[MasterItem]:
    return filter_by_category(rows, category)


@router.get("/masters/items/dimension-values", response_model=MasterItemDimensionValuesOut)
def list_master_item_dimension_values(
    kind: Literal["materials", "thicknesses", "colors", "embosses", "item_codes"] = Query(
        ...,
        description="materials | thicknesses | colors | embosses | item_codes",
    ),
    material_name: Optional[str] = Query(None, description="Wajib untuk thicknesses, colors, embosses, item_codes"),
    thickness_text: Optional[str] = Query(None, description="Wajib untuk colors, embosses, item_codes"),
    color: Optional[str] = Query(None, description="Wajib untuk embosses & item_codes"),
    emboss: Optional[str] = Query(None, description="Opsional untuk item_codes"),
    category: Optional[str] = Query(None, description="Filter kategori master: PU | Suede | SubKon"),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> MasterItemDimensionValuesOut:
    if kind == "materials" and not category:
        names = [
            str(n).strip()
            for n in db.scalars(
                select(MasterItem.material_name)
                .where(
                    MasterItem.material_name.is_not(None),
                    MasterItem.material_name != "",
                )
                .distinct()
            ).all()
            if n
        ]
        values = sorted({n for n in names if n}, key=str.lower)
        return MasterItemDimensionValuesOut(values=values)
    if kind == "materials":
        name_rows = list(
            db.execute(
                select(MasterItem.material_name, MasterItem.category).where(
                    MasterItem.material_name.is_not(None),
                    MasterItem.material_name != "",
                )
            ).all()
        )
        slim = [
            type("DimRow", (), {"material_name": n, "category": c})()
            for n, c in name_rows
        ]
        slim = _filter_master_items_by_category(slim, category)
        return MasterItemDimensionValuesOut(values=distinct_material_names(slim))
    rows = _filter_master_items_by_category(
        list(db.scalars(select(MasterItem).order_by(MasterItem.item_code)).all()),
        category,
    )
    if kind == "thicknesses":
        if not (material_name and str(material_name).strip()):
            raise HTTPException(status_code=400, detail="material_name wajib untuk kind=thicknesses")
        return MasterItemDimensionValuesOut(values=distinct_thicknesses(rows, material_name))
    if kind == "colors":
        if not (material_name and str(material_name).strip()) or not (thickness_text and str(thickness_text).strip()):
            raise HTTPException(
                status_code=400,
                detail="material_name dan thickness_text wajib untuk kind=colors",
            )
        return MasterItemDimensionValuesOut(values=distinct_colors(rows, material_name, thickness_text))
    if kind == "embosses":
        if (
            not (material_name and str(material_name).strip())
            or not (thickness_text and str(thickness_text).strip())
            or not (color and str(color).strip())
        ):
            raise HTTPException(
                status_code=400,
                detail="material_name, thickness_text, dan color wajib untuk kind=embosses",
            )
        return MasterItemDimensionValuesOut(values=distinct_embosses(rows, material_name, thickness_text, color))
    if kind == "item_codes":
        if (
            not (material_name and str(material_name).strip())
            or not (thickness_text and str(thickness_text).strip())
            or not (color and str(color).strip())
        ):
            raise HTTPException(
                status_code=400,
                detail="material_name, thickness_text, dan color wajib untuk kind=item_codes",
            )
        return MasterItemDimensionValuesOut(
            values=distinct_item_codes(rows, material_name, thickness_text, color, emboss),
        )
    raise HTTPException(status_code=400, detail="kind tidak valid")


@router.get("/masters/items/resolve-by-dimensions", response_model=MasterItemResolveByDimensionsOut)
def resolve_master_item_by_dimensions(
    material_name: str = Query(..., min_length=1),
    thickness_text: str = Query(..., min_length=1),
    color: str = Query(..., min_length=1),
    emboss: Optional[str] = Query(None, description="Filter emboss jika ada beberapa FG"),
    category: Optional[str] = Query(None, description="Filter kategori master: PU | Suede | SubKon"),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> MasterItemResolveByDimensionsOut:
    rows = _filter_master_items_by_category(
        list(db.scalars(select(MasterItem).order_by(MasterItem.item_code)).all()),
        category,
    )
    hits = resolve_by_dimensions(
        rows,
        material_name=material_name,
        thickness_text=thickness_text,
        color=color,
        emboss=emboss,
    )
    if not hits:
        return MasterItemResolveByDimensionsOut(status="none")
    if len(hits) == 1:
        return MasterItemResolveByDimensionsOut(status="single", item=MasterItemOut.model_validate(hits[0]))
    return MasterItemResolveByDimensionsOut(
        status="ambiguous",
        candidates=[MasterItemOut.model_validate(r) for r in hits],
    )


@router.get("/masters/items/next-code", response_model=MasterItemNextCodeOut)
def next_master_item_code(
    category: str = Query(..., description="PU | Suede | SubKon"),
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> MasterItemNextCodeOut:
    return MasterItemNextCodeOut(item_code=allocate_next_item_code(db, category))


@router.get("/masters/items/swatch-cascade", response_model=MasterItemSwatchCascadeOut)
def master_item_swatch_cascade(
    material_name: Optional[str] = Query(None),
    color: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> MasterItemSwatchCascadeOut:
    embosses, _matched = list_swatch_embosses(db, material_name=material_name, color=color)
    return MasterItemSwatchCascadeOut(
        materials=list_swatch_materials(db),
        colors=list_swatch_colors(db, material_name),
        embosses=embosses,
    )


@router.get("/masters/items/swatch-embosses", response_model=MasterItemSwatchEmbossOut)
def master_item_swatch_embosses(
    material_name: Optional[str] = Query(None),
    color: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> MasterItemSwatchEmbossOut:
    embosses, matched_color = list_swatch_embosses(db, material_name=material_name, color=color)
    return MasterItemSwatchEmbossOut(embosses=embosses, matched_color=matched_color)


@router.post("/masters/items", response_model=MasterItemOut)
def create_master_item(
    body: MasterItemCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> MasterItem:
    data = body.model_dump(exclude_unset=True)
    row = MasterItem(
        item_code=allocate_next_item_code(db, data.get("category")),
        category=data.get("category"),
        material_name=data.get("material_name"),
        thickness_range=data.get("thickness_range"),
        color=data.get("color"),
        emboss=data.get("emboss"),
        flag_color_black=bool(data.get("flag_color_black")),
        flag_color=bool(data.get("flag_color")),
        flag_flourasent=bool(data.get("flag_flourasent")),
        flag_metalic=bool(data.get("flag_metalic")),
        flag_emboss=bool(data.get("flag_emboss")),
        flag_special_emboss=bool(data.get("flag_special_emboss")),
        # Kolom lama tetap ada di DB namun tidak dipakai lagi di input.
        thickness_mm=None,
        softness=None,
        color_reference=None,
        color_standard=None,
        backing=None,
        quantity_order_default=None,
        style_article=None,
        model=None,
        model_takedown=None,
        exim_material_code=None,
    )
    apply_item_color_extract(row)
    db.add(row)
    db.commit()
    db.refresh(row)
    return _annotate_item_color_links(db, [MasterItemOut.model_validate(row)])[0]


@router.put("/masters/items/{item_id}", response_model=MasterItemOut)
def update_master_item(
    item_id: int,
    body: MasterItemCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> MasterItem:
    row = db.get(MasterItem, item_id)
    if not row:
        raise HTTPException(status_code=404, detail="Master item tidak ditemukan")
    data = body.model_dump(exclude_unset=True)
    data.pop("item_code", None)
    for k, v in data.items():
        setattr(row, k, v)
    # Pastikan kolom lama dikosongkan agar konsisten dengan form baru.
    row.thickness_mm = None
    row.softness = None
    row.color_reference = None
    row.color_standard = None
    row.backing = None
    row.quantity_order_default = None
    row.style_article = None
    row.model = None
    row.model_takedown = None
    row.exim_material_code = None
    apply_item_color_extract(row)
    db.commit()
    db.refresh(row)
    return _annotate_item_color_links(db, [MasterItemOut.model_validate(row)])[0]


@router.delete("/masters/items/{item_id}")
def delete_master_item(
    item_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> dict[str, str]:
    row = db.get(MasterItem, item_id)
    if not row:
        raise HTTPException(status_code=404, detail="Master item tidak ditemukan")
    
    from app.models import PoDetail
    
    related_details = db.query(PoDetail).filter(PoDetail.master_item_id == item_id).count()
    if related_details > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Master item '{row.item_code}' tidak bisa dihapus karena masih direferensikan di {related_details} PO detail (material_name tetap tersimpan di PO)"
        )
    
    db.delete(row)
    db.commit()
    return {"status": "deleted"}


@router.get("/masters/items/export")
async def export_master_items(
    template: bool = Query(False, description="Jika true, unduh template kosong (header saja)"),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    if template:
        excel_content = export_master_items_template_xlsx()
        filename = "master_items_template.xlsx"
    else:
        excel_content = export_master_items_xlsx(db)
        filename = "master_items.xlsx"
    return StreamingResponse(
        io.BytesIO(excel_content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/masters/items/import")
async def import_master_items(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="File Excel kosong")
    try:
        result = import_master_items_xlsx(db, content)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Gagal import: bentrok item_code unik di database. Periksa duplikat di file.",
        ) from e
    except Exception:
        db.rollback()
        raise
    return result.to_dict()


# --- Master Harga (matrix USD) ---
@router.get("/masters/prices", response_model=list[MasterPriceOut])
def list_master_prices(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> list[MasterPrice]:
    return list(
        db.scalars(select(MasterPrice).order_by(MasterPrice.id.asc())).all()
    )


@router.post("/masters/import-zip")
async def import_master_zip(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> dict:
    """Import master data dari ZIP berisi CSV:

    - 00_Master_Customer.csv (customer_code, customer_name, phone, address)
    - 01_Master_Item.csv (item_code, thickness_mm, material_name, emboss, color, category)
    - 02_Master_Harga.csv (sesuai kolom MasterPrice)
    """
    raw = await file.read()
    try:
        z = zipfile.ZipFile(io.BytesIO(raw))
    except Exception as e:
        logger.error(f"Error in import_master_zip: {e}")
        raise HTTPException(status_code=400, detail="File harus ZIP") from e

    stats = {"customers_upserted": 0, "items_upserted": 0, "prices_upserted": 0, "files": []}

    def dec(v: Optional[str]) -> Optional[Decimal]:
        if v is None:
            return None
        s = str(v).strip()
        if not s:
            return None
        try:
            return Decimal(s)
        except Exception:
            return None

    for name in z.namelist():
        base = name.split("/")[-1]
        if not base.lower().endswith(".csv"):
            continue
        stats["files"].append(base)
        data = z.read(name)
        text = data.decode("utf-8-sig", errors="ignore")
        reader = csv.DictReader(io.StringIO(text))

        if base.startswith("00_") or "master_customer" in base.lower():
            for r in reader:
                code = (r.get("customer_code") or r.get("code") or "").strip()
                if not code:
                    continue
                row = db.scalars(select(Customer).where(Customer.code == code)).first()
                if not row:
                    row = Customer(code=code)
                    db.add(row)
                row.name = (r.get("customer_name") or r.get("name") or row.name)
                row.phone = (r.get("phone") or row.phone)
                row.address = (r.get("address") or row.address)
                stats["customers_upserted"] += 1

        elif base.startswith("01_") or "master_item" in base.lower():
            for r in reader:
                item_code = (r.get("item_code") or "").strip()
                if not item_code:
                    continue
                row = db.scalars(select(MasterItem).where(MasterItem.item_code == item_code)).first()
                if not row:
                    row = MasterItem(item_code=item_code)
                    db.add(row)
                category_raw = (r.get("category") or "").strip().lower()
                category_alias = {
                    "pu": "PU",
                    "suide": "Suede",
                    "suede": "Suede",
                    "subkon": "SubKon",
                    "subcont": "SubKon",
                    "subcontract": "SubKon",
                }
                row.category = category_alias.get(category_raw, row.category or "PU")
                row.material_name = (r.get("material_name") or row.material_name)
                row.thickness_range = (r.get("thickness_range") or row.thickness_range)
                row.emboss = (r.get("emboss") or row.emboss)
                row.color = (r.get("color") or row.color)
                row.thickness_mm = None
                row.softness = None
                row.color_reference = None
                row.color_standard = None
                row.backing = None
                row.quantity_order_default = None
                row.style_article = None
                row.model = None
                row.model_takedown = None
                row.exim_material_code = None
                apply_item_color_extract(row)
                stats["items_upserted"] += 1

        elif base.startswith("02_") or "master_harga" in base.lower() or "master_harga" in base.lower():
            for r in reader:
                line_no = r.get("line_no")
                tier = (r.get("price_tier") or "").strip() or None
                mname = (r.get("material_name") or "").strip() or None
                trange = (r.get("thickness_range") or "").strip() or None
                q = select(MasterPrice)
                if line_no:
                    try:
                        q = q.where(MasterPrice.line_no == int(line_no))
                    except Exception:
                        pass
                if tier:
                    q = q.where(MasterPrice.price_tier == tier)
                if mname:
                    q = q.where(MasterPrice.material_name == mname)
                if trange:
                    q = q.where(MasterPrice.thickness_range == trange)
                row = db.scalars(q).first()
                if not row:
                    row = MasterPrice()
                    db.add(row)
                row.line_no = int(line_no) if line_no and str(line_no).isdigit() else row.line_no
                row.material_category = r.get("material_category") or row.material_category
                row.material_type = r.get("material_type") or row.material_type
                row.material_name = mname or row.material_name
                row.thickness_range = trange or row.thickness_range
                price_white_usd = dec(r.get("price_white_usd"))
                if price_white_usd is not None:
                    row.price_white_usd = price_white_usd
                price_black_usd = dec(r.get("price_black_usd"))
                if price_black_usd is not None:
                    row.price_black_usd = price_black_usd
                price_color_usd = dec(r.get("price_color_usd"))
                if price_color_usd is not None:
                    row.price_color_usd = price_color_usd
                price_metallic_usd = dec(r.get("price_metallic_usd"))
                if price_metallic_usd is not None:
                    row.price_metallic_usd = price_metallic_usd
                row.remark = r.get("remark") or row.remark
                row.price_tier = tier or row.price_tier
                stats["prices_upserted"] += 1

    db.commit()
    return {"status": "ok", **stats}
