from datetime import datetime
from typing import Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Brand, BrandConstraint, Customer, CustomerBrandMapping
from app.schemas import (
    BrandConstraintCreate,
    BrandConstraintOut,
    BrandConstraintUpdate,
    BrandOut,
    CustomerBrandMappingCreate,
    CustomerBrandMappingOut,
    CustomerBrandMappingUpdate,
    CustomerCreate,
    CustomerOut,
    CustomerUpdate,
)
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
    
    from app.models import PoHeader, Invoice, DeliveryHeader, BuyerPriceList
    
    errors = []
    
    related_pos = db.query(PoHeader).filter(PoHeader.customer_id == customer_id).count()
    if related_pos > 0:
        errors.append(f"{related_pos} PO")
    
    related_invoices = db.query(Invoice).filter(Invoice.customer_id == customer_id).count()
    if related_invoices > 0:
        errors.append(f"{related_invoices} Invoice")
    
    related_deliveries = db.query(DeliveryHeader).filter(DeliveryHeader.customer_id == customer_id).count()
    if related_deliveries > 0:
        errors.append(f"{related_deliveries} Delivery")
    
    if errors:
        raise HTTPException(
            status_code=400, 
            detail=f"Customer tidak bisa dihapus karena masih memiliki: {', '.join(errors)}"
        )
    
    db.delete(row)
    db.commit()
    return {"status": "deleted"}


@router.get("/customers/{customer_id}/brand-mappings", response_model=list[CustomerBrandMappingOut])
def list_brand_mappings(
    customer_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> list[CustomerBrandMapping]:
    row = db.get(Customer, customer_id)
    if not row:
        raise HTTPException(status_code=404, detail="Customer tidak ditemukan")
    stmt = select(CustomerBrandMapping).where(CustomerBrandMapping.customer_id == customer_id)
    return list(db.scalars(stmt).all())


@router.post("/customers/{customer_id}/brand-mappings", response_model=CustomerBrandMappingOut)
def create_brand_mapping(
    customer_id: int,
    body: CustomerBrandMappingCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing")),
) -> CustomerBrandMapping:
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer tidak ditemukan")
    brand = db.get(Brand, body.brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand tidak ditemukan")
    existing = db.scalars(
        select(CustomerBrandMapping).where(
            CustomerBrandMapping.customer_id == customer_id,
            CustomerBrandMapping.brand_id == body.brand_id,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Mapping sudah ada")
    if body.is_default:
        db.scalars(
            select(CustomerBrandMapping).where(
                CustomerBrandMapping.customer_id == customer_id,
                CustomerBrandMapping.is_default == True,
            )
        ).first()
        for m in db.scalars(
            select(CustomerBrandMapping).where(
                CustomerBrandMapping.customer_id == customer_id,
                CustomerBrandMapping.is_default == True,
            )
        ).all():
            m.is_default = False
    mapping = CustomerBrandMapping(customer_id=customer_id, **body.model_dump())
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping


@router.put("/customers/{customer_id}/brand-mappings/{mapping_id}", response_model=CustomerBrandMappingOut)
def update_brand_mapping(
    customer_id: int,
    mapping_id: int,
    body: CustomerBrandMappingUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing")),
) -> CustomerBrandMapping:
    mapping = db.get(CustomerBrandMapping, mapping_id)
    if not mapping or mapping.customer_id != customer_id:
        raise HTTPException(status_code=404, detail="Mapping tidak ditemukan")
    if body.is_default is True:
        for m in db.scalars(
            select(CustomerBrandMapping).where(
                CustomerBrandMapping.customer_id == customer_id,
                CustomerBrandMapping.is_default == True,
                CustomerBrandMapping.id != mapping_id,
            )
        ).all():
            m.is_default = False
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(mapping, k, v)
    db.commit()
    db.refresh(mapping)
    return mapping


@router.delete("/customers/{customer_id}/brand-mappings/{mapping_id}")
def delete_brand_mapping(
    customer_id: int,
    mapping_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing")),
) -> dict[str, str]:
    mapping = db.get(CustomerBrandMapping, mapping_id)
    if not mapping or mapping.customer_id != customer_id:
        raise HTTPException(status_code=404, detail="Mapping tidak ditemukan")
    db.delete(mapping)
    db.commit()
    return {"status": "deleted"}


@router.get("/customers/{customer_id}/allowed-brands", response_model=list[BrandOut])
def get_allowed_brands(
    customer_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> list[Brand]:
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer tidak ditemukan")
    constraint = db.scalars(
        select(BrandConstraint).where(BrandConstraint.customer_id == customer_id)
    ).first()
    if constraint and constraint.allowed_brand_ids:
        stmt = select(Brand).where(Brand.id.in_(constraint.allowed_brand_ids))
    else:
        stmt = select(Brand)
    return list(db.scalars(stmt).all())


@router.get("/customers/{customer_id}/brand-constraint", response_model=Optional[BrandConstraintOut])
def get_brand_constraint(
    customer_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> Optional[BrandConstraint]:
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer tidak ditemukan")
    constraint = db.scalars(
        select(BrandConstraint).where(BrandConstraint.customer_id == customer_id)
    ).first()
    if not constraint:
        return None
    return constraint


@router.put("/customers/{customer_id}/brand-constraint", response_model=BrandConstraintOut)
def upsert_brand_constraint(
    customer_id: int,
    body: Union[BrandConstraintCreate, BrandConstraintUpdate],
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing")),
) -> BrandConstraint:
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer tidak ditemukan")
    constraint = db.scalars(
        select(BrandConstraint).where(BrandConstraint.customer_id == customer_id)
    ).first()
    if constraint:
        for k, v in body.model_dump(exclude_unset=True).items():
            setattr(constraint, k, v)
    else:
        constraint = BrandConstraint(customer_id=customer_id, **body.model_dump())
        db.add(constraint)
    db.commit()
    db.refresh(constraint)
    return constraint
