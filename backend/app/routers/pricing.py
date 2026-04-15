from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import SpecialPrice, CustomerSpecialPrice
from app.schemas import SpecialPriceCreate, SpecialPriceUpdate, SpecialPriceOut, CustomerSpecialPriceCreate, CustomerSpecialPriceUpdate, CustomerSpecialPriceOut

router = APIRouter(prefix="/pricing", tags=["pricing"])


@router.get("/special-prices", response_model=list[SpecialPriceOut])
def list_special_prices(buyer_code: str = None, db: Session = Depends(get_db)):
    query = db.query(SpecialPrice).filter(SpecialPrice.is_active == True)
    if buyer_code:
        query = query.filter(SpecialPrice.buyer_code == buyer_code)
    return query.order_by(SpecialPrice.id.desc()).all()


@router.post("/special-prices", response_model=SpecialPriceOut)
def create_special_price(body: SpecialPriceCreate, db: Session = Depends(get_db)):
    row = SpecialPrice(**body.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/special-prices/{price_id}", response_model=SpecialPriceOut)
def update_special_price(price_id: int, body: SpecialPriceUpdate, db: Session = Depends(get_db)):
    row = db.query(SpecialPrice).get(price_id)
    if not row:
        raise HTTPException(404, "Special price not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/special-prices/{price_id}")
def delete_special_price(price_id: int, db: Session = Depends(get_db)):
    row = db.query(SpecialPrice).get(price_id)
    if not row:
        raise HTTPException(404, "Special price not found")
    row.is_active = False
    db.commit()
    return {"status": "deleted"}


@router.get("/customer-prices", response_model=list[CustomerSpecialPriceOut])
def list_customer_prices(customer_id: int = None, db: Session = Depends(get_db)):
    query = db.query(CustomerSpecialPrice).filter(CustomerSpecialPrice.is_active == True)
    if customer_id:
        query = query.filter(CustomerSpecialPrice.customer_id == customer_id)
    return query.order_by(CustomerSpecialPrice.id.desc()).all()


@router.post("/customer-prices", response_model=CustomerSpecialPriceOut)
def create_customer_price(body: CustomerSpecialPriceCreate, db: Session = Depends(get_db)):
    row = CustomerSpecialPrice(**body.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/customer-prices/{price_id}", response_model=CustomerSpecialPriceOut)
def update_customer_price(price_id: int, body: CustomerSpecialPriceUpdate, db: Session = Depends(get_db)):
    row = db.query(CustomerSpecialPrice).get(price_id)
    if not row:
        raise HTTPException(404, "Customer special price not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/customer-prices/{price_id}")
def delete_customer_price(price_id: int, db: Session = Depends(get_db)):
    row = db.query(CustomerSpecialPrice).get(price_id)
    if not row:
        raise HTTPException(404, "Customer special price not found")
    row.is_active = False
    db.commit()
    return {"status": "deleted"}
