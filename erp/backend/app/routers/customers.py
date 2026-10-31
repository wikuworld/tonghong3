import io
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.customer_excel import (
    export_customers_template_xlsx,
    export_customers_xlsx,
    import_customers_xlsx,
)
from app.timeutil import app_now
from app.models import Brand, BrandConstraint, Customer, CustomerBrandMapping, CustomerPic
from app.paging import apply_sort, page_dict, parse_page_params
from app.schemas import (
    # BrandConstraintCreate,  # tulis constraint halaman mapping, disembunyikan sementara
    BrandConstraintOut,
    # BrandConstraintUpdate,
    BrandOut,
    # CustomerBrandMappingCreate,  # tulis mapping halaman mapping, disembunyikan sementara
    # CustomerBrandMappingOut,
    # CustomerBrandMappingUpdate,
    CustomerCreate,
    CustomerOut,
    CustomerPageOut,
    CustomerUpdate,
)
from app.routers.auth import get_current_user, require_roles

router = APIRouter(tags=["customers"])


@router.get("/customers/resolve", response_model=Optional[CustomerOut])
def resolve_customer(
    q: str = Query(..., min_length=1, description="Nama atau kode customer"),
    create: bool = Query(False, description="Buat customer jika belum ada (service/admin)"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> Optional[Customer]:
    """Resolve customer by exact name/code (case-insensitive). Optional create for MRP service."""
    from app.routers.auth import is_service_mrp
    import re

    raw = (q or "").strip()
    if not raw or raw == "-":
        return None
    needle = " ".join(raw.lower().split())
    rows = list(db.scalars(select(Customer).order_by(Customer.id.asc()).limit(5000)).all())
    for row in rows:
        name_n = " ".join(str(row.name or "").strip().lower().split())
        code_n = " ".join(str(row.code or "").strip().lower().split())
        if name_n == needle or code_n == needle:
            return row
    if not create:
        return None
    if user.role not in {"admin", "marketing", "sales"} and not is_service_mrp(user):
        raise HTTPException(status_code=403, detail="Akses ditolak untuk create customer")
    base = re.sub(r"[^A-Z0-9]+", "-", raw.upper()).strip("-")[:24] or "CUST"
    code = f"MRP-{base}"
    if db.scalars(select(Customer).where(Customer.code == code).limit(1)).first():
        code = f"{code}-{abs(hash(raw)) % 10000}"
    row = Customer(code=code, name=raw[:255], is_active=True)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


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
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=200),
    limit: Optional[int] = Query(None, ge=1, le=100),
    offset: Optional[int] = Query(None, ge=0),
    sort_by: Optional[str] = Query(None, description="name|code|created_at|id"),
    sort_dir: Optional[str] = Query(None),
    _user=Depends(get_current_user),
) -> dict:
    params = parse_page_params(
        page=page,
        page_size=page_size,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_dir=sort_dir,
        default_page_size=20,
        max_page_size=100,
    )
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
    stmt = apply_sort(
        stmt,
        sortable={
            "name": Customer.name,
            "code": Customer.code,
            "created_at": Customer.created_at,
            "id": Customer.id,
        },
        sort_by=params.sort_by,
        sort_dir=params.sort_dir,
        default_order=(Customer.id.desc(),),
    )
    items = list(db.scalars(stmt.limit(params.limit).offset(params.offset)).all())
    return page_dict(items=items, total=total, params=params)


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


@router.get("/customers/export")
def export_customers(
    template: bool = Query(False, description="Jika true, unduh template kosong (header saja)"),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    if template:
        excel_content = export_customers_template_xlsx()
        filename = "customer_template.xlsx"
    else:
        excel_content = export_customers_xlsx(db)
        filename = "customer.xlsx"
    return StreamingResponse(
        io.BytesIO(excel_content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/customers/import")
async def import_customers(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing", "sales")),
):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="File Excel kosong")
    try:
        result = import_customers_xlsx(db, content)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return result.to_dict()


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
    row.updated_at = app_now()
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


@router.get("/customers/{customer_id:int}/brand-mappings")
def list_brand_mappings(
    customer_id: int,
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=200),
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    sort_by: Optional[str] = Query(None, description="id|brand_id|is_default|created_at"),
    sort_dir: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    row = db.get(Customer, customer_id)
    if not row:
        raise HTTPException(status_code=404, detail="Customer tidak ditemukan")
    params = parse_page_params(
        page=page,
        page_size=page_size,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_dir=sort_dir or "asc",
        default_page_size=50,
    )
    stmt = select(CustomerBrandMapping).where(CustomerBrandMapping.customer_id == customer_id)
    count_stmt = select(func.count(CustomerBrandMapping.id)).where(
        CustomerBrandMapping.customer_id == customer_id
    )
    total = int(db.scalar(count_stmt) or 0)
    stmt = apply_sort(
        stmt,
        sortable={
            "id": CustomerBrandMapping.id,
            "brand_id": CustomerBrandMapping.brand_id,
            "is_default": CustomerBrandMapping.is_default,
            "created_at": CustomerBrandMapping.created_at,
        },
        sort_by=params.sort_by,
        sort_dir=params.sort_dir,
        default_order=(CustomerBrandMapping.is_default.desc(), CustomerBrandMapping.id.asc()),
    )
    from sqlalchemy.orm import selectinload

    items = list(
        db.scalars(
            stmt.options(selectinload(CustomerBrandMapping.brand))
            .limit(params.limit)
            .offset(params.offset)
        ).all()
    )
    return page_dict(items=items, total=total, params=params)


# Disembunyikan sementara: tulis mapping hanya dipakai halaman Mapping Customer-Brand.
# @router.post("/customers/{customer_id:int}/brand-mappings", response_model=CustomerBrandMappingOut)
# def create_brand_mapping(
#     customer_id: int,
#     body: CustomerBrandMappingCreate,
#     db: Session = Depends(get_db),
#     _user=Depends(require_roles("admin", "marketing")),
# ) -> CustomerBrandMapping:
#     customer = db.get(Customer, customer_id)
#     if not customer:
#         raise HTTPException(status_code=404, detail="Customer tidak ditemukan")
#     brand = db.get(Brand, body.brand_id)
#     if not brand:
#         raise HTTPException(status_code=404, detail="Brand tidak ditemukan")
#     existing = db.scalars(
#         select(CustomerBrandMapping).where(
#             CustomerBrandMapping.customer_id == customer_id,
#             CustomerBrandMapping.brand_id == body.brand_id,
#         )
#     ).first()
#     if existing:
#         raise HTTPException(status_code=409, detail="Mapping sudah ada")
#     if body.is_default:
#         db.scalars(
#             select(CustomerBrandMapping).where(
#                 CustomerBrandMapping.customer_id == customer_id,
#                 CustomerBrandMapping.is_default,
#             )
#         ).first()
#         for m in db.scalars(
#             select(CustomerBrandMapping).where(
#                 CustomerBrandMapping.customer_id == customer_id,
#                 CustomerBrandMapping.is_default,
#             )
#         ).all():
#             m.is_default = False
#     mapping = CustomerBrandMapping(customer_id=customer_id, **body.model_dump())
#     db.add(mapping)
#     db.commit()
#     db.refresh(mapping)
#     return mapping
#
#
# @router.put("/customers/{customer_id:int}/brand-mappings/{mapping_id:int}", response_model=CustomerBrandMappingOut)
# def update_brand_mapping(
#     customer_id: int,
#     mapping_id: int,
#     body: CustomerBrandMappingUpdate,
#     db: Session = Depends(get_db),
#     _user=Depends(require_roles("admin", "marketing")),
# ) -> CustomerBrandMapping:
#     mapping = db.get(CustomerBrandMapping, mapping_id)
#     if not mapping or mapping.customer_id != customer_id:
#         raise HTTPException(status_code=404, detail="Mapping tidak ditemukan")
#     if body.is_default is True:
#         for m in db.scalars(
#             select(CustomerBrandMapping).where(
#                 CustomerBrandMapping.customer_id == customer_id,
#                 CustomerBrandMapping.is_default,
#                 CustomerBrandMapping.id != mapping_id,
#             )
#         ).all():
#             m.is_default = False
#     for k, v in body.model_dump(exclude_unset=True).items():
#         setattr(mapping, k, v)
#     db.commit()
#     db.refresh(mapping)
#     return mapping
#
#
# @router.delete("/customers/{customer_id:int}/brand-mappings/{mapping_id:int}")
# def delete_brand_mapping(
#     customer_id: int,
#     mapping_id: int,
#     db: Session = Depends(get_db),
#     _user=Depends(require_roles("admin", "marketing")),
# ) -> dict[str, str]:
#     mapping = db.get(CustomerBrandMapping, mapping_id)
#     if not mapping or mapping.customer_id != customer_id:
#         raise HTTPException(status_code=404, detail="Mapping tidak ditemukan")
#     db.delete(mapping)
#     db.commit()
#     return {"status": "deleted"}


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
            return []
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


# Disembunyikan sementara: simpan constraint hanya dipakai halaman Mapping Customer-Brand.
# @router.put("/customers/{customer_id:int}/brand-constraint", response_model=BrandConstraintOut)
# def upsert_brand_constraint(
#     customer_id: int,
#     body: Union[BrandConstraintCreate, BrandConstraintUpdate],
#     db: Session = Depends(get_db),
#     _user=Depends(require_roles("admin", "marketing")),
# ) -> BrandConstraint:
#     customer = db.get(Customer, customer_id)
#     if not customer:
#         raise HTTPException(status_code=404, detail="Customer tidak ditemukan")
#     constraint = db.scalars(
#         select(BrandConstraint).where(BrandConstraint.customer_id == customer_id)
#     ).first()
#     if constraint:
#         for k, v in body.model_dump(exclude_unset=True).items():
#             setattr(constraint, k, v)
#     else:
#         constraint = BrandConstraint(customer_id=customer_id, **body.model_dump())
#         db.add(constraint)
#     db.commit()
#     db.refresh(constraint)
#     return constraint
