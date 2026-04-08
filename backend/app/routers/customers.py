from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Customer
from app.schemas import CustomerCreate, CustomerOut, CustomerUpdate
from app.routers.auth import get_current_user, require_roles

router = APIRouter(tags=["customers"])


@router.get("/customers", response_model=list[CustomerOut])
def list_customers(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Search code/name/email"),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    _user=Depends(get_current_user),
) -> list[Customer]:
    stmt = select(Customer).order_by(Customer.id.desc()).limit(limit).offset(offset)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            or_(
                Customer.code.ilike(like),
                Customer.name.ilike(like),
                Customer.email.ilike(like),
            )
        )
    return list(db.scalars(stmt).all())


@router.post("/customers", response_model=CustomerOut)
def create_customer(
    body: CustomerCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing", "sales")),
) -> Customer:
    row = Customer(**body.model_dump(exclude_unset=True))
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/customers/{customer_id}", response_model=CustomerOut)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> Customer:
    row = db.get(Customer, customer_id)
    if not row:
        raise HTTPException(status_code=404, detail="Customer tidak ditemukan")
    return row


@router.put("/customers/{customer_id}", response_model=CustomerOut)
def update_customer(
    customer_id: int,
    body: CustomerUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing", "sales")),
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
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> dict[str, str]:
    row = db.get(Customer, customer_id)
    if not row:
        raise HTTPException(status_code=404, detail="Customer tidak ditemukan")
    db.delete(row)
    db.commit()
    return {"status": "deleted"}
