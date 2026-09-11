from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from decimal import Decimal, InvalidOperation
import csv
import io
from app.db import get_db
from app.models import BuyerPriceList
from app.routers.auth import require_roles

router = APIRouter(prefix="/pricing", tags=["pricing"])


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
