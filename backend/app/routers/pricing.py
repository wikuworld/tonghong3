from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from decimal import Decimal, InvalidOperation
import csv
import io
from app.db import get_db
from app.models import SpecialPrice, CustomerSpecialPrice, BuyerPriceList
from app.routers.auth import get_current_user, require_roles
from app.schemas import SpecialPriceCreate, SpecialPriceUpdate, SpecialPriceOut, CustomerSpecialPriceCreate, CustomerSpecialPriceUpdate, CustomerSpecialPriceOut

router = APIRouter(prefix="/pricing", tags=["pricing"])


@router.get("/special-prices", response_model=list[SpecialPriceOut])
def list_special_prices(
    buyer_code: str = None,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    query = db.query(SpecialPrice).filter(SpecialPrice.is_active)
    if buyer_code:
        query = query.filter(SpecialPrice.buyer_code == buyer_code)
    return query.order_by(SpecialPrice.id.desc()).all()


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
    row = db.query(SpecialPrice).get(price_id)
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
    row = db.query(SpecialPrice).get(price_id)
    if not row:
        raise HTTPException(404, "Special price not found")
    row.is_active = False
    db.commit()
    return {"status": "deleted"}


@router.get("/customer-prices", response_model=list[CustomerSpecialPriceOut])
def list_customer_prices(
    customer_id: int = None,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    query = db.query(CustomerSpecialPrice).filter(CustomerSpecialPrice.is_active)
    if customer_id:
        query = query.filter(CustomerSpecialPrice.customer_id == customer_id)
    return query.order_by(CustomerSpecialPrice.id.desc()).all()


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
    row = db.query(CustomerSpecialPrice).get(price_id)
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
    row = db.query(CustomerSpecialPrice).get(price_id)
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
