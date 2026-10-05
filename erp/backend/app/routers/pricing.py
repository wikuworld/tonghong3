from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from decimal import Decimal, InvalidOperation
import csv
import io
from app.db import get_db
from app.models import SpecialPrice, CustomerSpecialPrice, BuyerPriceList
from app.paging import apply_sort, page_dict, parse_page_params
from app.routers.auth import get_current_user, require_roles
from app.schemas import (
    SpecialPriceCreate,
    SpecialPriceUpdate,
    SpecialPriceOut,
    CustomerSpecialPriceCreate,
    CustomerSpecialPriceUpdate,
    CustomerSpecialPriceOut,
)

router = APIRouter(prefix="/pricing", tags=["pricing"])


@router.get("/special-prices")
def list_special_prices(
    buyer_code: Optional[str] = None,
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=200),
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    sort_by: Optional[str] = Query(None, description="id|buyer_code|discount_value|created_at"),
    sort_dir: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    params = parse_page_params(
        page=page,
        page_size=page_size,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_dir=sort_dir or "desc",
    )
    stmt = select(SpecialPrice).where(SpecialPrice.is_active.is_(True))
    count_stmt = select(func.count(SpecialPrice.id)).where(SpecialPrice.is_active.is_(True))
    if buyer_code:
        stmt = stmt.where(SpecialPrice.buyer_code == buyer_code)
        count_stmt = count_stmt.where(SpecialPrice.buyer_code == buyer_code)
    total = int(db.scalar(count_stmt) or 0)
    stmt = apply_sort(
        stmt,
        sortable={
            "id": SpecialPrice.id,
            "buyer_code": SpecialPrice.buyer_code,
            "discount_value": SpecialPrice.discount_value,
            "created_at": SpecialPrice.created_at,
            "discount_type": SpecialPrice.discount_type,
        },
        sort_by=params.sort_by,
        sort_dir=params.sort_dir,
        default_order=(SpecialPrice.id.desc(),),
    )
    items = list(db.scalars(stmt.limit(params.limit).offset(params.offset)).all())
    return page_dict(items=items, total=total, params=params)


@router.post("/special-prices", response_model=SpecialPriceOut)
def create_special_price(
    body: SpecialPriceCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing")),
):
    row = SpecialPrice(**body.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/special-prices/{price_id}", response_model=SpecialPriceOut)
def update_special_price(
    price_id: int,
    body: SpecialPriceUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing")),
):
    row = db.get(SpecialPrice, price_id)
    if not row:
        raise HTTPException(404, "Special price not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/special-prices/{price_id}")
def delete_special_price(
    price_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
):
    row = db.get(SpecialPrice, price_id)
    if not row:
        raise HTTPException(404, "Special price not found")
    row.is_active = False
    db.commit()
    return {"status": "deleted"}


@router.get("/customer-prices")
def list_customer_prices(
    customer_id: Optional[int] = None,
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=200),
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    sort_by: Optional[str] = Query(None, description="id|buyer_code|customer_id|created_at|valid_from"),
    sort_dir: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    params = parse_page_params(
        page=page,
        page_size=page_size,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_dir=sort_dir or "desc",
    )
    stmt = (
        select(CustomerSpecialPrice)
        .options(selectinload(CustomerSpecialPrice.customer))
        .where(CustomerSpecialPrice.is_active.is_(True))
    )
    count_stmt = select(func.count(CustomerSpecialPrice.id)).where(
        CustomerSpecialPrice.is_active.is_(True)
    )
    if customer_id:
        stmt = stmt.where(CustomerSpecialPrice.customer_id == customer_id)
        count_stmt = count_stmt.where(CustomerSpecialPrice.customer_id == customer_id)
    total = int(db.scalar(count_stmt) or 0)
    stmt = apply_sort(
        stmt,
        sortable={
            "id": CustomerSpecialPrice.id,
            "buyer_code": CustomerSpecialPrice.buyer_code,
            "customer_id": CustomerSpecialPrice.customer_id,
            "created_at": CustomerSpecialPrice.created_at,
            "valid_from": CustomerSpecialPrice.valid_from,
            "price_override": CustomerSpecialPrice.price_override,
        },
        sort_by=params.sort_by,
        sort_dir=params.sort_dir,
        default_order=(CustomerSpecialPrice.id.desc(),),
    )
    items = list(db.scalars(stmt.limit(params.limit).offset(params.offset)).all())
    return page_dict(items=items, total=total, params=params)


@router.post("/customer-prices", response_model=CustomerSpecialPriceOut)
def create_customer_price(
    body: CustomerSpecialPriceCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing")),
):
    row = CustomerSpecialPrice(**body.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/customer-prices/{price_id}", response_model=CustomerSpecialPriceOut)
def update_customer_price(
    price_id: int,
    body: CustomerSpecialPriceUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing")),
):
    row = db.get(CustomerSpecialPrice, price_id)
    if not row:
        raise HTTPException(404, "Customer special price not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/customer-prices/{price_id}")
def delete_customer_price(
    price_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
):
    row = db.get(CustomerSpecialPrice, price_id)
    if not row:
        raise HTTPException(404, "Customer special price not found")
    row.is_active = False
    db.commit()
    return {"status": "deleted"}


class PriceUpdateItem(BaseModel):
    buyer_code: str
    material_pattern: str
    new_price: Decimal


class BulkPriceUpdate(BaseModel):
    updates: list[PriceUpdateItem]


def _get_price_columns(meta_json: dict | None) -> list[str]:
    """Extract price-related column keys from BuyerPriceList meta_json."""
    if not meta_json:
        return ['PRICE', 'UOM', 'PRICE USD']
    columns = meta_json.get('columns', [])
    price_cols = [col.get('key') for col in columns if col.get('is_price') is True]
    return price_cols if price_cols else ['PRICE', 'UOM', 'PRICE USD']


@router.post("/bulk-update", response_model=dict)
def bulk_update_prices(
    body: BulkPriceUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing")),
):
    """Update multiple prices at once."""
    updated = 0
    for item in body.updates:
        buyer_list = db.query(BuyerPriceList).filter(
            BuyerPriceList.buyer_code == item.buyer_code
        ).first()

        if buyer_list and buyer_list.rows:
            meta = buyer_list.meta_json or {}
            price_columns = _get_price_columns(meta)
            for row in buyer_list.rows:
                cells = row.cells or {}
                material = cells.get('ITEM', '') or cells.get('MATERIAL', '')
                if item.material_pattern.lower() in material.lower():
                    for price_col in price_columns:
                        if price_col in cells:
                            cells[price_col] = str(item.new_price)
                    row.cells = cells
                    updated += 1

    db.commit()
    return {"updated": updated}


@router.post("/bulk-update-csv")
async def bulk_update_prices_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing")),
):
    """Bulk update from CSV file."""
    content = await file.read()
    decoded = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))

    updated = 0
    for row in reader:
        buyer_code = row.get('buyer_code', '').strip()
        material_pattern = row.get('material_pattern', '').strip()
        new_price = row.get('new_price', '').strip()

        if not buyer_code or not material_pattern or not new_price:
            continue

        try:
            new_price_dec = Decimal(new_price)
        except (InvalidOperation, ValueError):
            continue

        buyer_list = db.query(BuyerPriceList).filter(
            BuyerPriceList.buyer_code == buyer_code
        ).first()

        if buyer_list and buyer_list.rows:
            meta = buyer_list.meta_json or {}
            price_columns = _get_price_columns(meta)
            for bprow in buyer_list.rows:
                cells = bprow.cells or {}
                material = cells.get('ITEM', '') or cells.get('MATERIAL', '')
                if material_pattern.lower() in material.lower():
                    for price_col in price_columns:
                        if price_col in cells:
                            cells[price_col] = str(new_price_dec)
                    bprow.cells = cells
                    updated += 1

    db.commit()
    return {"updated": updated}
