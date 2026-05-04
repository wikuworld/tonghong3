from datetime import datetime
from typing import Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Brand, BrandConstraint, Customer, CustomerBrandMapping, CustomerPic
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
    CustomerPageOut,
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
                Customer.payment_terms.ilike(like),
                Customer.reference_quotation.ilike(like),
            )
        )
    return list(db.scalars(stmt).all())


@router.get("/customers/page", response_model=CustomerPageOut)
def list_customers_page(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Search all customer fields"),
    is_export_customer: Optional[bool] = Query(None, description="Filter export vs lokal"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _user=Depends(get_current_user),
) -> CustomerPageOut:
    stmt = select(Customer)
    count_stmt = select(func.count(Customer.id))
    if is_export_customer is not None:
        stmt = stmt.where(Customer.is_export_customer == is_export_customer)
        count_stmt = count_stmt.where(Customer.is_export_customer == is_export_customer)
    if q:
        like = f"%{q}%"
        where_clause = or_(
            Customer.code.ilike(like),
            Customer.name.ilike(like),
            Customer.email.ilike(like),
            Customer.contact_person.ilike(like),
            Customer.position.ilike(like),
            Customer.phone.ilike(like),
            Customer.country.ilike(like),
            Customer.tax_id.ilike(like),
            Customer.address.ilike(like),
            Customer.billing_address.ilike(like),
            Customer.reference_quotation.ilike(like),
            Customer.payment_terms.ilike(like),
            Customer.remark.ilike(like),
        )
        stmt = stmt.where(where_clause)
        count_stmt = count_stmt.where(where_clause)
    total = int(db.scalar(count_stmt) or 0)
    items = list(
        db.scalars(stmt.order_by(Customer.id.desc()).limit(limit).offset(offset)).all()
    )
    return CustomerPageOut(items=items, total=total, limit=limit, offset=offset)


@router.post("/customers", response_model=CustomerOut)
def create_customer(
    body: CustomerCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing", "sales")),
) -> Customer:
    payload = body.model_dump(exclude_unset=True)
    contacts_payload = payload.pop("contacts", [])
    row = Customer(**payload)
    for c in contacts_payload:
        row.contacts.append(CustomerPic(**c))
    if row.contacts:
        first = row.contacts[0]
        row.contact_person = first.name
        row.position = first.title
        row.phone = first.phone
        row.email = first.email
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/customers/{customer_id:int}", response_model=CustomerOut)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> Customer:
    row = db.get(Customer, customer_id)
    if not row:
        raise HTTPException(status_code=404, detail="Customer tidak ditemukan")
    return row


@router.put("/customers/{customer_id:int}", response_model=CustomerOut)
def update_customer(
    customer_id: int,
    body: CustomerUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing", "sales")),
) -> Customer:
    row = db.get(Customer, customer_id)
    if not row:
        raise HTTPException(status_code=404, detail="Customer tidak ditemukan")
    updates = body.model_dump(exclude_unset=True)
    contacts_payload = updates.pop("contacts", None)
    for k, v in updates.items():
        setattr(row, k, v)
    if contacts_payload is not None:
        row.contacts.clear()
        for c in contacts_payload:
            row.contacts.append(CustomerPic(**c))
        first = row.contacts[0] if row.contacts else None
        row.contact_person = first.name if first else None
        row.position = first.title if first else None
        row.phone = first.phone if first else None
        row.email = first.email if first else None
    row.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(row)
    return row


@router.delete("/customers/{customer_id:int}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> dict[str, str]:
    row = db.get(Customer, customer_id)
    if not row:
        raise HTTPException(status_code=404, detail="Customer tidak ditemukan")
    
    from app.models import PoHeader, Invoice, DeliveryHeader
    
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


@router.get("/customers/{customer_id:int}/brand-mappings", response_model=list[CustomerBrandMappingOut])
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


@router.post("/customers/{customer_id:int}/brand-mappings", response_model=CustomerBrandMappingOut)
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
                CustomerBrandMapping.is_default,
            )
        ).first()
        for m in db.scalars(
            select(CustomerBrandMapping).where(
                CustomerBrandMapping.customer_id == customer_id,
                CustomerBrandMapping.is_default,
            )
        ).all():
            m.is_default = False
    mapping = CustomerBrandMapping(customer_id=customer_id, **body.model_dump())
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping


@router.put("/customers/{customer_id:int}/brand-mappings/{mapping_id:int}", response_model=CustomerBrandMappingOut)
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
                CustomerBrandMapping.is_default,
                CustomerBrandMapping.id != mapping_id,
            )
        ).all():
            m.is_default = False
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(mapping, k, v)
    db.commit()
    db.refresh(mapping)
    return mapping


@router.delete("/customers/{customer_id:int}/brand-mappings/{mapping_id:int}")
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


@router.get("/customers/{customer_id:int}/allowed-brands", response_model=list[BrandOut])
def get_allowed_brands(
    customer_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> list[Brand]:
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer tidak ditemukan")
    mapped_brand_ids = [
        int(x)
        for x in db.scalars(
            select(CustomerBrandMapping.brand_id).where(
                CustomerBrandMapping.customer_id == customer_id
            )
        ).all()
        if x is not None
    ]
    if mapped_brand_ids:
        stmt = select(Brand).where(Brand.id.in_(sorted(set(mapped_brand_ids))))
    else:
        constraint = db.scalars(
            select(BrandConstraint).where(BrandConstraint.customer_id == customer_id)
        ).first()
        if constraint and constraint.allowed_brand_ids:
            stmt = select(Brand).where(Brand.id.in_(constraint.allowed_brand_ids))
        else:
            stmt = select(Brand)
    return list(db.scalars(stmt).all())


@router.get("/customers/{customer_id:int}/brand-constraint", response_model=Optional[BrandConstraintOut])
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


@router.put("/customers/{customer_id:int}/brand-constraint", response_model=BrandConstraintOut)
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
