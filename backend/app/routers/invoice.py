from datetime import date, datetime, timedelta
from email.message import EmailMessage
import smtplib
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.config import settings
from app.models import Customer, DeliveryHeader, Invoice, InvoiceDetail
from app.schemas import InvoiceCreate, InvoiceDetailCreate, InvoiceUpdate, row_to_dict
from app.services.business_rules import validate_invoice_against_delivery
from app.services.mkt_workflow import sync_invoice_billing_from_delivery
from app.routers.auth import get_current_user, require_roles
from app.services.audit import log_change

router = APIRouter(tags=["invoice"])


@router.post("/invoice")
def create_invoice(
    body: InvoiceCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "finance")),
) -> dict:
    validate_invoice_against_delivery(db, body.delivery_id, body.po_number)
    data = body.model_dump(exclude_unset=True)
    row = Invoice(**data)
    db.add(row)
    db.flush()
    log_change(
        db,
        entity_type="invoice",
        entity_id=row.id,
        action="create",
        after={"invoice_number": row.invoice_number, "delivery_id": row.delivery_id},
        actor=user.username,
    )
    sync_invoice_billing_from_delivery(db, body.delivery_id)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.get("/invoice")
def list_invoice(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Search invoice no/PO/customer"),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    _user=Depends(get_current_user),
) -> list[dict]:
    stmt = select(Invoice).order_by(Invoice.id.desc()).limit(limit).offset(offset)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            and_(
                Invoice.id.is_not(None),
                (
                    (Invoice.invoice_number.ilike(like))
                    | (Invoice.po_number.ilike(like))
                    | (Invoice.customer_name.ilike(like))
                ),
            )
        )
    rows = db.scalars(stmt).all()
    return [row_to_dict(r) for r in rows]


@router.get("/invoice/outstanding")
def list_outstanding_invoice(
    db: Session = Depends(get_db),
    overdue_only: bool = Query(False),
    due_within_days: Optional[int] = Query(None, ge=0, le=365),
    hide_po: bool = Query(False),
    _user=Depends(get_current_user),
) -> list[dict]:
    today = date.today()
    stmt = select(Invoice).order_by(Invoice.id.desc())
    if overdue_only:
        stmt = stmt.where(and_(Invoice.due_date.is_not(None), Invoice.due_date < today))
    elif due_within_days is not None:
        stmt = stmt.where(
            and_(
                Invoice.due_date.is_not(None),
                Invoice.due_date >= today,
                Invoice.due_date <= (today + timedelta(days=int(due_within_days))),
            )
        )
    rows = db.scalars(stmt).all()
    out: list[dict] = []
    for r in rows:
        x = row_to_dict(r)
        if hide_po:
            x["po_number"] = None
        out.append(x)
    return out


@router.get("/invoice/{invoice_id}")
def get_invoice(
    invoice_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> dict:
    row = db.get(Invoice, invoice_id)
    if not row:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
    return row_to_dict(row)


@router.put("/invoice/{invoice_id}")
def update_invoice(
    invoice_id: int,
    body: InvoiceUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "finance")),
) -> dict:
    row = db.get(Invoice, invoice_id)
    if not row:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
    before = {
        "due_date": row.due_date,
        "tax_invoice_no": row.tax_invoice_no,
        "tax_invoice_date": row.tax_invoice_date,
        "receipt_no": row.receipt_no,
        "received_by": row.received_by,
        "received_date": row.received_date,
        "nopen": row.nopen,
        "nomor_aju": row.nomor_aju,
    }
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    log_change(
        db,
        entity_type="invoice",
        entity_id=row.id,
        action="update",
        before=before,
        after={
            "due_date": row.due_date,
            "tax_invoice_no": row.tax_invoice_no,
            "tax_invoice_date": row.tax_invoice_date,
            "receipt_no": row.receipt_no,
            "received_by": row.received_by,
            "received_date": row.received_date,
            "nopen": row.nopen,
            "nomor_aju": row.nomor_aju,
        },
        actor=user.username,
    )
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


def _send_email(to_email: str, subject: str, body: str) -> None:
    if not settings.smtp_host or not settings.smtp_from:
        raise HTTPException(status_code=500, detail="SMTP belum dikonfigurasi (smtp_host/smtp_from)")
    msg = EmailMessage()
    msg["From"] = settings.smtp_from
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)
    if settings.smtp_tls:
        with smtplib.SMTP(settings.smtp_host, int(settings.smtp_port)) as s:
            s.starttls()
            if settings.smtp_user:
                s.login(settings.smtp_user, settings.smtp_password)
            s.send_message(msg)
    else:
        with smtplib.SMTP(settings.smtp_host, int(settings.smtp_port)) as s:
            if settings.smtp_user:
                s.login(settings.smtp_user, settings.smtp_password)
            s.send_message(msg)


@router.post("/invoice/reminders/run")
def run_invoice_reminders(
    db: Session = Depends(get_db),
    mode: str = Query("overdue", description="overdue | due_soon"),
    days: int = Query(None, ge=0, le=365),
    user=Depends(require_roles("admin", "finance")),
) -> dict:
    today = date.today()
    if days is None:
        days = int(settings.invoice_reminder_days_before or 7)
    if mode not in ("overdue", "due_soon"):
        raise HTTPException(status_code=400, detail="mode harus overdue atau due_soon")

    stmt = (
        select(Invoice, DeliveryHeader, Customer)
        .join(DeliveryHeader, DeliveryHeader.id == Invoice.delivery_id)
        .join(Customer, Customer.id == DeliveryHeader.customer_id)
        .where(Invoice.due_date.is_not(None))
    )
    if mode == "overdue":
        stmt = stmt.where(Invoice.due_date < today)
    else:
        stmt = stmt.where(and_(Invoice.due_date >= today, Invoice.due_date <= (today + timedelta(days=int(days)))))

    rows = db.execute(stmt.order_by(Invoice.id.desc())).all()
    sent = 0
    skipped = 0
    errors: list[str] = []
    for inv, dh, cust in rows:
        if not cust.email:
            skipped += 1
            continue
        subj = f"[Tonghong] Reminder Invoice {inv.invoice_number or inv.id}"
        body = "\n".join(
            [
                f"Yth. {cust.name or 'Customer'},",
                "",
                "Ini pengingat invoice:",
                f"- Invoice: {inv.invoice_number or inv.id}",
                f"- Tanggal invoice: {inv.invoice_date or ''}",
                f"- Jatuh tempo: {inv.due_date or ''}",
                f"- Delivery: {dh.delivery_number or dh.id}",
                "",
                "Mohon konfirmasi pembayaran / status penerimaan dokumen.",
                "",
                f"Generated at: {datetime.utcnow().isoformat()}Z",
            ]
        )
        try:
            _send_email(str(cust.email), subj, body)
            sent += 1
        except Exception as e:
            errors.append(f"{inv.id}: {type(e).__name__} {e}")
    log_change(
        db,
        entity_type="invoice_reminder",
        entity_id=None,
        action=f"run_{mode}",
        after={"sent": sent, "skipped": skipped, "days": days},
        actor=user.username,
    )
    db.commit()
    return {"mode": mode, "days": days, "sent": sent, "skipped": skipped, "errors": errors[:20]}

@router.get("/invoice/{invoice_id}/details")
def list_invoice_details(
    invoice_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> list[dict]:
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
    invoice_id: int,
    body: InvoiceDetailCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "finance")),
) -> dict:
    inv = db.get(Invoice, invoice_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
    row = InvoiceDetail(invoice_id=invoice_id, **body.model_dump(exclude_unset=True))
    db.add(row)
    db.flush()
    log_change(
        db,
        entity_type="invoice_line",
        entity_id=row.id,
        action="create",
        after={"invoice_id": invoice_id, "item_description": row.item_description, "qty": row.qty},
        actor=user.username,
    )
    db.commit()
    db.refresh(row)
    return row_to_dict(row)
