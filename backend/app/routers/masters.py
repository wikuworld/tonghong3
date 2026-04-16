"""Master: Brand & Customer PIC (CR §3.1)."""

from __future__ import annotations

import csv
import io
import logging
import zipfile
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

logger = logging.getLogger(__name__)
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict
from app.schemas import MasterItemCreate, MasterItemOut, MasterPriceOut
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import (
    BrandBuyerMap,
    Brand,
    BuyerPriceList,
    Customer,
    CustomerPic,
    MasterItem,
    MasterPrice,
)
from app.routers.auth import get_current_user, require_roles
from app.utils.excel_utils import export_to_excel, import_from_excel

router = APIRouter(tags=["masters"])


class BrandIn(BaseModel):
    model_config = ConfigDict(extra="ignore")

    code: Optional[str] = None
    name: Optional[str] = None


class BrandOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: Optional[str] = None
    name: Optional[str] = None


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


@router.get("/masters/brands", response_model=list[BrandOut])
def list_brands(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> list[Brand]:
    return list(db.scalars(select(Brand).order_by(Brand.id.desc())).all())


@router.post("/masters/brands", response_model=BrandOut)
def create_brand(
    body: BrandIn,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> Brand:
    row = Brand(**body.model_dump(exclude_unset=True))
    db.add(row)
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
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
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


@router.post("/masters/items", response_model=MasterItemOut)
def create_master_item(
    body: MasterItemCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> MasterItem:
    row = MasterItem(**body.model_dump(exclude_unset=True))
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
    columns = ["item_code", "material_name", "thickness_range", "thickness_mm",
               "color", "emboss", "softness", "color_reference", "backing",
               "style_article", "model", "category", "exim_material_code"]
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
    columns = ["item_code", "material_name", "thickness_range", "thickness_mm",
               "color", "emboss", "softness", "color_reference", "backing",
               "style_article", "model", "category", "exim_material_code"]
    
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
                thickness_mm = dec(r.get("thickness_mm"))
                if thickness_mm is not None:
                    row.thickness_mm = thickness_mm
                row.material_name = (r.get("material_name") or row.material_name)
                row.emboss = (r.get("emboss") or row.emboss)
                row.color = (r.get("color") or row.color)
                row.softness = (r.get("softness") or row.softness)
                row.color_reference = (
                    r.get("color_reference")
                    or r.get("color_standard")
                    or row.color_reference
                )
                row.backing = (r.get("backing") or row.backing)
                qty_default = dec(
                    r.get("quantity_order_default")
                    or r.get("qty_default")
                    or r.get("quantity_order")
                )
                if qty_default is not None:
                    row.quantity_order_default = qty_default
                row.style_article = (r.get("style_article") or row.style_article)
                row.model = (r.get("model") or row.model)
                row.category = (r.get("category") or row.category)
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
