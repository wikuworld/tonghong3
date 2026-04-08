from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Invoice, InvoiceDetail
from app.schemas import InvoiceCreate, InvoiceDetailCreate, row_to_dict
from app.services.business_rules import validate_invoice_against_delivery
from app.services.mkt_workflow import sync_invoice_billing_from_delivery

router = APIRouter(tags=["invoice"])


@router.post("/invoice")
def create_invoice(body: InvoiceCreate, db: Session = Depends(get_db)) -> dict:
    validate_invoice_against_delivery(db, body.delivery_id, body.po_number)
    data = body.model_dump(exclude_unset=True)
    row = Invoice(**data)
    db.add(row)
    db.flush()
    sync_invoice_billing_from_delivery(db, body.delivery_id)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.get("/invoice")
def list_invoice(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.scalars(select(Invoice).order_by(Invoice.id.desc())).all()
    return [row_to_dict(r) for r in rows]


@router.get("/invoice/{invoice_id}")
def get_invoice(invoice_id: int, db: Session = Depends(get_db)) -> dict:
    row = db.get(Invoice, invoice_id)
    if not row:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
    return row_to_dict(row)


@router.get("/invoice/{invoice_id}/details")
def list_invoice_details(invoice_id: int, db: Session = Depends(get_db)) -> list[dict]:
    if not db.get(Invoice, invoice_id):
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
    rows = db.scalars(
        select(InvoiceDetail)
        .where(InvoiceDetail.invoice_id == invoice_id)
        .order_by(InvoiceDetail.id.asc())
    ).all()
    return [row_to_dict(r) for r in rows]


@router.post("/invoice/{invoice_id}/details")
def add_invoice_detail(
    invoice_id: int, body: InvoiceDetailCreate, db: Session = Depends(get_db)
) -> dict:
    inv = db.get(Invoice, invoice_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
    row = InvoiceDetail(invoice_id=invoice_id, **body.model_dump(exclude_unset=True))
    db.add(row)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)
