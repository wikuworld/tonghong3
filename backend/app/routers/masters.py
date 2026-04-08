"""Master: Brand & Customer PIC (CR §3.1)."""

from __future__ import annotations

import csv
import io
import zipfile
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, ConfigDict
from app.schemas import MasterItemCreate, MasterItemOut, MasterPriceOut
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Brand, Customer, CustomerPic, MasterItem, MasterPrice
from app.routers.auth import get_current_user, require_roles

router = APIRouter(tags=["masters"])


class BrandIn(BaseModel):
    model_config = ConfigDict(extra="ignore")

    customer_id: Optional[int] = None
    code: Optional[str] = None
    name: Optional[str] = None


class BrandOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: Optional[int] = None
    code: Optional[str] = None
    name: Optional[str] = None


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
    db.delete(row)
    db.commit()
    return {"status": "deleted"}


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
