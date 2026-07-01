"""Master: Brand & Customer PIC (CR §3.1)."""

from __future__ import annotations

import csv
import io
import logging
import zipfile
from decimal import Decimal
from typing import Literal, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

logger = logging.getLogger(__name__)
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field
from app.schemas import (
    MasterItemCreate,
    MasterItemDimensionValuesOut,
    MasterItemOut,
    MasterItemResolveByDimensionsOut,
    MasterPriceOut,
)
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import (
    BrandBuyerMap,
    Brand,
    BuyerPriceList,
    Customer,
    CustomerBrandMapping,
    CustomerPic,
    FluorescentColorMaster,
    MasterItem,
    MasterPrice,
)
from app.routers.auth import get_current_user, require_roles
from app.utils.excel_utils import export_to_excel, import_from_excel
from app.services.fluorescent_color import (
    VALID_COLOR_CLASSES,
    apply_fluorescent_fields,
    find_existing,
    gather_bundled_rows,
    parse_fluorescent_upload,
    upsert_fluorescent_rows,
)
from app.services.master_item_dimensions import (
    distinct_colors,
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
    season_label: Optional[str] = None
    season_year: Optional[int] = None
    season_type: Optional[str] = None
    color_name: str
    color_code: Optional[str] = None
    color_class: str
    source_file: Optional[str] = None
    is_active: bool = True


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


@router.get("/masters/brands", response_model=list[BrandOut])
def list_brands(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> list[BrandOut]:
    brands = list(db.scalars(select(Brand).order_by(Brand.id.desc())).all())
    out: list[BrandOut] = []
    for brand in brands:
        mapped_ids = sorted({int(m.customer_id) for m in (brand.customer_mappings or []) if m.customer_id is not None})
        out.append(
            BrandOut(
                id=brand.id,
                code=brand.code,
                name=brand.name,
                customer_id=mapped_ids[0] if mapped_ids else None,
                customer_ids=mapped_ids,
            )
        )
    return out


@router.post("/masters/brands", response_model=BrandOut)
def create_brand(
    body: BrandIn,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> Brand:
    brand_name = (body.name or "").strip()
    if not brand_name:
        raise HTTPException(status_code=400, detail="Nama brand wajib diisi")
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
    return row


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
        row.name = brand_name
        # Tetap sinkronkan code dari nama agar modul lama tidak putus.
        row.code = brand_name
    if "customer_ids" in data:
        customer_ids = sorted({int(x) for x in (data.get("customer_ids") or []) if x is not None})
        db.query(CustomerBrandMapping).filter(CustomerBrandMapping.brand_id == brand_id).delete()
        for customer_id in customer_ids:
            customer = db.get(Customer, customer_id)
            if customer:
                db.add(CustomerBrandMapping(customer_id=customer_id, brand_id=brand_id, is_default=False))
    db.commit()
    db.refresh(row)
    return row


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
    buyer_codes = db.scalars(select(BuyerPriceList.buyer_code)).all()
    created = 0
    mapped = 0
    for code in sorted({str(x).strip() for x in buyer_codes if str(x).strip()}):
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
    db.query(BrandBuyerMap).filter(BrandBuyerMap.brand_id == brand_id).delete()
    cleaned = sorted({str(code).strip() for code in body.buyer_codes if str(code).strip()})
    for code in cleaned:
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
    items = list(
        db.scalars(
            stmt.order_by(
                FluorescentColorMaster.buyer_code.asc(),
                FluorescentColorMaster.season_year.desc(),
                FluorescentColorMaster.color_name.asc(),
            ).limit(limit).offset(offset)
        ).all()
    )
    return FluorescentColorPageOut(items=items, total=total, limit=limit, offset=offset)


@router.get("/masters/fluorescent-colors/form-options", response_model=FluorescentColorFormOptionsOut)
def fluorescent_color_form_options(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> FluorescentColorFormOptionsOut:
    """Opsi dropdown form tambah/edit fluorescent — dari master buyer & data existing."""
    rows = list(
        db.scalars(
            select(FluorescentColorMaster).where(FluorescentColorMaster.is_active.is_(True))
        ).all()
    )
    buyer_codes: set[str] = {"GLOBAL", "NB", "ADIDAS", "UA", "NIKE", "PUMA", "REEBOK"}
    for bb in db.scalars(select(BrandBuyerMap.buyer_code).distinct()).all():
        if bb:
            buyer_codes.add(str(bb).strip().upper())

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
    for key, val in data.items():
        setattr(row, key, val)
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
    db.commit()
    return {"status": "deactivated"}


@router.post("/masters/fluorescent-colors/import-bundled", response_model=FluorescentImportResultOut)
def import_fluorescent_bundled(
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
    stats = upsert_fluorescent_rows(db, rows)
    return FluorescentImportResultOut(**stats)


@router.post("/masters/fluorescent-colors/import-csv", response_model=FluorescentImportResultOut)
async def import_fluorescent_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing")),
) -> FluorescentImportResultOut:
    """Upload CSV fluorescent (format NB/ADIDAS/GLOBAL/UA atau kolom generic)."""
    raw = await file.read()
    filename = file.filename or "upload.csv"
    rows = parse_fluorescent_upload(raw, filename)
    if not rows:
        raise HTTPException(status_code=400, detail="Tidak ada baris valid dalam file CSV")
    stats = upsert_fluorescent_rows(db, rows)
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
@router.get("/masters/items", response_model=list[MasterItemOut])
def list_master_items(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> list[MasterItem]:
    return list(db.scalars(select(MasterItem).order_by(MasterItem.item_code)).all())


def _filter_master_items_by_category(
    rows: list[MasterItem],
    category: Optional[str],
) -> list[MasterItem]:
    return filter_by_category(rows, category)


@router.get("/masters/items/dimension-values", response_model=MasterItemDimensionValuesOut)
def list_master_item_dimension_values(
    kind: Literal["materials", "thicknesses", "colors"] = Query(..., description="materials | thicknesses | colors"),
    material_name: Optional[str] = Query(None, description="Wajib untuk thicknesses & colors"),
    thickness_text: Optional[str] = Query(None, description="Wajib untuk colors"),
    category: Optional[str] = Query(None, description="Filter kategori master: PU | Suide | SubKon"),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> MasterItemDimensionValuesOut:
    rows = _filter_master_items_by_category(
        list(db.scalars(select(MasterItem).order_by(MasterItem.item_code)).all()),
        category,
    )
    if kind == "materials":
        return MasterItemDimensionValuesOut(values=distinct_material_names(rows))
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
    raise HTTPException(status_code=400, detail="kind tidak valid")


@router.get("/masters/items/resolve-by-dimensions", response_model=MasterItemResolveByDimensionsOut)
def resolve_master_item_by_dimensions(
    material_name: str = Query(..., min_length=1),
    thickness_text: str = Query(..., min_length=1),
    color: str = Query(..., min_length=1),
    category: Optional[str] = Query(None, description="Filter kategori master: PU | Suide | SubKon"),
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
    )
    if not hits:
        return MasterItemResolveByDimensionsOut(status="none")
    if len(hits) == 1:
        return MasterItemResolveByDimensionsOut(status="single", item=MasterItemOut.model_validate(hits[0]))
    return MasterItemResolveByDimensionsOut(
        status="ambiguous",
        candidates=[MasterItemOut.model_validate(r) for r in hits],
    )


@router.post("/masters/items", response_model=MasterItemOut)
def create_master_item(
    body: MasterItemCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> MasterItem:
    data = body.model_dump(exclude_unset=True)
    row = MasterItem(
        item_code=data.get("item_code"),
        category=data.get("category"),
        material_name=data.get("material_name"),
        thickness_range=data.get("thickness_range"),
        color=data.get("color"),
        emboss=data.get("emboss"),
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
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


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
    if "item_code" in data and str(data["item_code"]).strip() != row.item_code:
        exists = db.scalars(
            select(MasterItem).where(MasterItem.item_code == str(data["item_code"]).strip())
        ).first()
        if exists and exists.id != item_id:
            raise HTTPException(status_code=400, detail="item_code sudah dipakai")
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
    db.commit()
    db.refresh(row)
    return row


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
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    items = db.scalars(select(MasterItem).order_by(MasterItem.item_code)).all()
    columns = ["category", "item_code", "material_name", "thickness_range", "color", "emboss"]
    data = [{col: getattr(item, col, None) for col in columns} for item in items]
    excel_content = export_to_excel(data, columns, "Master Items")
    return StreamingResponse(
        io.BytesIO(excel_content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=master_items.xlsx"}
    )


@router.post("/masters/items/import")
async def import_master_items(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
):
    columns = ["category", "item_code", "material_name", "thickness_range", "color", "emboss"]
    
    content = await file.read()
    items = import_from_excel(content, columns)
    
    imported = 0
    for item_data in items:
        existing = db.scalars(select(MasterItem).where(
            MasterItem.item_code == item_data.get("item_code")
        )).first()
        
        if existing:
            for col in columns:
                val = item_data.get(col)
                if val and hasattr(existing, col):
                    setattr(existing, col, val)
        else:
            new_item = MasterItem(item_code=item_data.get("item_code"))
            for col in columns:
                val = item_data.get(col)
                if val and hasattr(new_item, col):
                    setattr(new_item, col, val)
            db.add(new_item)
        imported += 1
    
    db.commit()
    return {"imported": imported}


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
                    "suide": "Suide",
                    "suede": "Suide",
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
