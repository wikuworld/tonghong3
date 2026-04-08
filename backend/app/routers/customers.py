from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Customer
from app.schemas import CustomerCreate, CustomerOut, CustomerUpdate

router = APIRouter(tags=["customers"])


@router.get("/customers", response_model=list[CustomerOut])
def list_customers(db: Session = Depends(get_db)) -> list[Customer]:
    return list(db.scalars(select(Customer).order_by(Customer.id.desc())).all())


@router.post("/customers", response_model=CustomerOut)
def create_customer(body: CustomerCreate, db: Session = Depends(get_db)) -> Customer:
    row = Customer(**body.model_dump(exclude_unset=True))
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/customers/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db)) -> Customer:
    row = db.get(Customer, customer_id)
    if not row:
        raise HTTPException(status_code=404, detail="Customer tidak ditemukan")
    return row


@router.put("/customers/{customer_id}", response_model=CustomerOut)
def update_customer(
    customer_id: int, body: CustomerUpdate, db: Session = Depends(get_db)
) -> Customer:
    row = db.get(Customer, customer_id)
    if not row:
        raise HTTPException(status_code=404, detail="Customer tidak ditemukan")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    row.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(row)
    return row


@router.delete("/customers/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    row = db.get(Customer, customer_id)
    if not row:
        raise HTTPException(status_code=404, detail="Customer tidak ditemukan")
    db.delete(row)
    db.commit()
    return {"status": "deleted"}
