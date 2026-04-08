"""Master: Brand & Customer PIC (CR §3.1)."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from app.schemas import MasterItemCreate, MasterItemOut, MasterPriceOut
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Brand, CustomerPic, MasterItem, MasterPrice

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
def list_brands(db: Session = Depends(get_db)) -> list[Brand]:
    return list(db.scalars(select(Brand).order_by(Brand.id.desc())).all())


@router.post("/masters/brands", response_model=BrandOut)
def create_brand(body: BrandIn, db: Session = Depends(get_db)) -> Brand:
    row = Brand(**body.model_dump(exclude_unset=True))
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/masters/brands/{brand_id}", response_model=BrandOut)
def update_brand(
    brand_id: int, body: BrandIn, db: Session = Depends(get_db)
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
def delete_brand(brand_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    row = db.get(Brand, brand_id)
    if not row:
        raise HTTPException(status_code=404, detail="Brand tidak ada")
    db.delete(row)
    db.commit()
    return {"status": "deleted"}


@router.get("/masters/customer-pics", response_model=list[PicOut])
def list_pics(db: Session = Depends(get_db)) -> list[CustomerPic]:
    return list(db.scalars(select(CustomerPic).order_by(CustomerPic.id.desc())).all())


@router.post("/masters/customer-pics", response_model=PicOut)
def create_pic(body: PicIn, db: Session = Depends(get_db)) -> CustomerPic:
    row = CustomerPic(**body.model_dump(exclude_unset=True))
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/masters/customer-pics/{pic_id}")
def delete_pic(pic_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    row = db.get(CustomerPic, pic_id)
    if not row:
        raise HTTPException(status_code=404, detail="PIC tidak ada")
    db.delete(row)
    db.commit()
    return {"status": "deleted"}


# --- Master Item (FG / sheet Master Item) ---
@router.get("/masters/items", response_model=list[MasterItemOut])
def list_master_items(db: Session = Depends(get_db)) -> list[MasterItem]:
    return list(db.scalars(select(MasterItem).order_by(MasterItem.item_code)).all())


@router.post("/masters/items", response_model=MasterItemOut)
def create_master_item(body: MasterItemCreate, db: Session = Depends(get_db)) -> MasterItem:
    row = MasterItem(**body.model_dump(exclude_unset=True))
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


# --- Master Harga (matrix USD) ---
@router.get("/masters/prices", response_model=list[MasterPriceOut])
def list_master_prices(db: Session = Depends(get_db)) -> list[MasterPrice]:
    return list(
        db.scalars(select(MasterPrice).order_by(MasterPrice.id.asc())).all()
    )
