from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import JournalEntry, AccountingMapping, PoHeader, Invoice
from app.routers.auth import get_current_user, require_roles
from app.schemas import JournalEntryOut, JournalEntryGenerate, TrialBalanceReport, TrialBalanceRow

router = APIRouter(prefix="/journal", tags=["journal"])


@router.get("/entries", response_model=list[JournalEntryOut])
def list_entries(
    date_from: date = Query(None),
    date_to: date = Query(None),
    transaction_type: str = Query(None),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    query = db.query(JournalEntry)
    if date_from:
        query = query.filter(JournalEntry.entry_date >= date_from)
    if date_to:
        query = query.filter(JournalEntry.entry_date <= date_to)
    if transaction_type:
        query = query.filter(JournalEntry.transaction_type == transaction_type)
    return query.order_by(JournalEntry.entry_date.desc(), JournalEntry.id.desc()).all()


@router.post("/entries/generate-from-transaction", response_model=list[JournalEntryOut])
def generate_from_transaction(
    body: JournalEntryGenerate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "finance")),
):
    if body.transaction_type == "po_created":
        return _generate_from_po(body.transaction_id, db)
    elif body.transaction_type == "invoice":
        return _generate_from_invoice(body.transaction_id, db)
    elif body.transaction_type == "payment":
        return _generate_from_payment(body.transaction_id, db)
    else:
        from fastapi import HTTPException
        raise HTTPException(400, f"Unknown transaction type: {body.transaction_type}")


def _generate_from_po(po_id: int, db: Session) -> list[JournalEntry]:
    po = db.query(PoHeader).get(po_id)
    if not po:
        from fastapi import HTTPException
        raise HTTPException(404, "PO not found")

    existing = db.query(JournalEntry).filter(
        JournalEntry.transaction_type == "po_created",
        JournalEntry.transaction_id == po_id,
    ).first()
    if existing:
        from fastapi import HTTPException
        raise HTTPException(409, "Journal entries already exist for this PO")

    mapping = db.query(AccountingMapping).filter(
        AccountingMapping.is_active.is_(True),
        AccountingMapping.transaction_type == "po_created",
    ).first()
    if not mapping:
        from fastapi import HTTPException
        raise HTTPException(400, "No accounting mapping found for po_created")

    entries = []
    total_amount = Decimal("0")
    for detail in po.details:
        if detail.unit_price and detail.quantity_order:
            total_amount += detail.unit_price * detail.quantity_order

    if total_amount > 0:
        entry_date = po.order_date or date.today()
        entry = JournalEntry(
            transaction_type="po_created",
            transaction_id=po_id,
            coa_code=mapping.coa_code,
            coa_name=mapping.coa_name,
            debit=total_amount,
            credit=Decimal("0"),
            description=f"PO {po.po_number}",
            entry_date=entry_date,
        )
        db.add(entry)
        entries.append(entry)

    db.commit()
    for e in entries:
        db.refresh(e)
    return entries


def _generate_from_invoice(invoice_id: int, db: Session) -> list[JournalEntry]:
    invoice = db.query(Invoice).get(invoice_id)
    if not invoice:
        from fastapi import HTTPException
        raise HTTPException(404, "Invoice not found")

    existing = db.query(JournalEntry).filter(
        JournalEntry.transaction_type == "invoice",
        JournalEntry.transaction_id == invoice_id,
    ).first()
    if existing:
        from fastapi import HTTPException
        raise HTTPException(409, "Journal entries already exist for this invoice")

    mapping = db.query(AccountingMapping).filter(
        AccountingMapping.is_active.is_(True),
        AccountingMapping.transaction_type == "invoice",
    ).first()
    if not mapping:
        from fastapi import HTTPException
        raise HTTPException(400, "No accounting mapping found for invoice")

    entries = []
    total_amount = invoice.total_amount or Decimal("0")

    if total_amount > 0:
        entry_date = invoice.invoice_date or date.today()
        entry = JournalEntry(
            transaction_type="invoice",
            transaction_id=invoice_id,
            coa_code=mapping.coa_code,
            coa_name=mapping.coa_name,
            debit=total_amount,
            credit=Decimal("0"),
            description=f"Invoice {invoice.invoice_number}",
            entry_date=entry_date,
        )
        db.add(entry)
        entries.append(entry)

    db.commit()
    for e in entries:
        db.refresh(e)
    return entries


def _generate_from_payment(invoice_id: int, db: Session) -> list[JournalEntry]:
    invoice = db.query(Invoice).get(invoice_id)
    if not invoice:
        from fastapi import HTTPException
        raise HTTPException(404, "Invoice not found")

    existing = db.query(JournalEntry).filter(
        JournalEntry.transaction_type == "payment",
        JournalEntry.transaction_id == invoice_id,
    ).first()
    if existing:
        from fastapi import HTTPException
        raise HTTPException(409, "Journal entries already exist for this payment")

    mapping = db.query(AccountingMapping).filter(
        AccountingMapping.is_active.is_(True),
        AccountingMapping.transaction_type == "payment",
    ).first()
    if not mapping:
        from fastapi import HTTPException
        raise HTTPException(400, "No accounting mapping found for payment")

    entries = []
    total_amount = invoice.total_amount or Decimal("0")

    if total_amount > 0:
        entry_date = invoice.payment_date or date.today()
        entry = JournalEntry(
            transaction_type="payment",
            transaction_id=invoice_id,
            coa_code=mapping.coa_code,
            coa_name=mapping.coa_name,
            debit=Decimal("0"),
            credit=total_amount,
            description=f"Payment for Invoice {invoice.invoice_number}",
            entry_date=entry_date,
        )
        db.add(entry)
        entries.append(entry)

    db.commit()
    for e in entries:
        db.refresh(e)
    return entries


@router.get("/entries/trial-balance", response_model=TrialBalanceReport)
def trial_balance(
    date_from: date = Query(None),
    date_to: date = Query(None),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    query = db.query(
        JournalEntry.coa_code,
        JournalEntry.coa_name,
        func.sum(JournalEntry.debit).label("total_debit"),
        func.sum(JournalEntry.credit).label("total_credit"),
    )
    if date_from:
        query = query.filter(JournalEntry.entry_date >= date_from)
    if date_to:
        query = query.filter(JournalEntry.entry_date <= date_to)
    
    query = query.group_by(
        JournalEntry.coa_code,
        JournalEntry.coa_name,
    )
    
    results = query.order_by(JournalEntry.coa_code).all()
    
    rows = []
    total_debit = Decimal("0")
    total_credit = Decimal("0")
    
    for r in results:
        debit = r.total_debit or Decimal("0")
        credit = r.total_credit or Decimal("0")
        rows.append(TrialBalanceRow(
            coa_code=r.coa_code,
            coa_name=r.coa_name,
            total_debit=debit,
            total_credit=credit,
        ))
        total_debit += debit
        total_credit += credit
    
    return TrialBalanceReport(
        as_of_date=date_to or date.today(),
        rows=rows,
        total_debit=total_debit,
        total_credit=total_credit,
        is_balanced=total_debit == total_credit,
    )
