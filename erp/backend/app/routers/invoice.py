from datetime import date, datetime, timedelta
from email.message import EmailMessage
import logging
import smtplib
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

logger = logging.getLogger(__name__)
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.timeutil import app_now
from app.config import settings
from app.models import Customer, DeliveryHeader, Invoice, InvoiceDetail, PoHeader
from app.paging import apply_sort, page_dict, parse_page_params, sort_mapped_rows
from app.schemas import (
    InvoiceCreate,
    InvoiceDetailCreate,
    InvoiceDetailOut,
    InvoiceOut,
    InvoicePageOut,
    InvoiceUpdate,
)
from app.services.business_rules import (
    joined_po_numbers_for_delivery,
    po_id_from_delivery,
    validate_invoice_against_delivery,
)
from app.services.mkt_workflow import sync_invoice_billing_from_delivery
from app.routers.auth import get_current_user, require_roles
from app.services.audit import log_change
from app.services.notifications import create_notification_for_roles
from app.services.document_numbers import allocate_invoice_number
from app.services.invoice_outstanding import (
    enrich_outstanding_invoice,
    exclude_voided_invoices,
    filter_outstanding_rows,
    invoice_ar_status,
    sync_payment_status_from_balance,
)
from app.services.accounts_receivable_report import invoice_balance
router = APIRouter(tags=["invoice"])


@router.post("/invoice", response_model=InvoiceOut)
def create_invoice(
    body: InvoiceCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "finance")),
) -> Invoice:
    validate_invoice_against_delivery(db, body.delivery_id, body.po_number)

    delivery = db.get(DeliveryHeader, body.delivery_id)

    data = body.model_dump(exclude_unset=True)

    if delivery and not data.get("customer_id"):
        data["customer_id"] = delivery.customer_id

    if not data.get("po_id"):
        resolved = po_id_from_delivery(db, body.delivery_id)
        if resolved:
            data["po_id"] = resolved

    if not (data.get("po_number") or "").strip():
        joined = joined_po_numbers_for_delivery(db, body.delivery_id)
        if joined:
            data["po_number"] = joined

    if not (data.get("invoice_number") or "").strip():
        po_for_num: PoHeader | None = None
        po_id = data.get("po_id")
        if po_id:
            po_for_num = db.get(PoHeader, int(po_id))
        inv_date = data.get("invoice_date") or (delivery.delivery_date if delivery else None)
        data["invoice_number"] = allocate_invoice_number(db, po=po_for_num, on_date=inv_date)

    row = Invoice(**data)
    db.add(row)
    db.flush()
    log_change(
        db,
        entity_type="invoice",
        entity_id=row.id,
        action="create",
        after={"invoice_number": row.invoice_number, "delivery_id": row.delivery_id, "customer_id": row.customer_id, "po_id": row.po_id},
        actor=user.username,
    )
    create_notification_for_roles(
        db,
        ("admin", "finance", "marketing"),
        title=f"Invoice {row.invoice_number or row.id} dibuat",
        message=f"Terhubung ke delivery ID {row.delivery_id}",
        category="invoice",
        entity_type="invoice",
        entity_id=row.id,
        route_path="/admin/invoice",
        route_query={"invoice_id": row.id},
    )
    sync_invoice_billing_from_delivery(db, body.delivery_id)
    from app.services.delivery_auto_invoice import sync_invoice_lines_from_delivery

    sync_invoice_lines_from_delivery(db, int(row.id), force=True)
    db.commit()
    db.refresh(row)
    return row


@router.get("/invoice", response_model=InvoicePageOut)
def list_invoice(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Search invoice no/PO/customer"),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    po_id: Optional[int] = Query(None, description="Filter by PO ID"),
    delivery_id: Optional[int] = Query(None, description="Filter by delivery ID"),
    payment_status: Optional[str] = Query(None, description="Filter by payment status"),
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=200),
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    sort_by: Optional[str] = Query(None, description="date|code|status|invoice_date|invoice_number|payment_status"),
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
    )
    stmt = select(Invoice)
    count_stmt = select(func.count(Invoice.id))
    stmt = exclude_voided_invoices(stmt)
    count_stmt = exclude_voided_invoices(count_stmt)

    if customer_id is not None:
        stmt = stmt.where(Invoice.customer_id == customer_id)
        count_stmt = count_stmt.where(Invoice.customer_id == customer_id)

    if po_id is not None:
        stmt = stmt.where(Invoice.po_id == po_id)
        count_stmt = count_stmt.where(Invoice.po_id == po_id)

    if delivery_id is not None:
        stmt = stmt.where(Invoice.delivery_id == delivery_id)
        count_stmt = count_stmt.where(Invoice.delivery_id == delivery_id)

    if payment_status:
        stmt = stmt.where(Invoice.payment_status == payment_status)
        count_stmt = count_stmt.where(Invoice.payment_status == payment_status)

    if q:
        like = f"%{q}%"
        where_q = and_(
            Invoice.id.is_not(None),
            (
                (Invoice.invoice_number.ilike(like))
                | (Invoice.po_number.ilike(like))
                | (Invoice.customer_name.ilike(like))
            ),
        )
        stmt = stmt.where(where_q)
        count_stmt = count_stmt.where(where_q)

    total = int(db.scalar(count_stmt) or 0)
    sortable = {
        "date": Invoice.invoice_date,
        "invoice_date": Invoice.invoice_date,
        "code": Invoice.invoice_number,
        "invoice_number": Invoice.invoice_number,
        "status": Invoice.payment_status,
        "payment_status": Invoice.payment_status,
        "id": Invoice.id,
    }
    stmt = apply_sort(
        stmt,
        sortable=sortable,
        sort_by=params.sort_by,
        sort_dir=params.sort_dir,
        default_order=(Invoice.id.desc(),),
    )
    items = list(db.scalars(stmt.limit(params.limit).offset(params.offset)).all())
    return page_dict(items=items, total=total, params=params)


@router.get("/invoice/outstanding", response_model=InvoicePageOut)
def list_outstanding_invoice(
    db: Session = Depends(get_db),
    overdue_only: bool = Query(False),
    due_within_days: Optional[int] = Query(None, ge=0, le=365),
    hide_po: bool = Query(False),
    open_only: bool = Query(True, description="Sembunyikan status Closed (saldo 0)"),
    ar_status: Optional[str] = Query(None, description="closed|overdue|not_overdue"),
    customer_id: Optional[int] = Query(None),
    q: Optional[str] = Query(None),
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=200),
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    sort_by: Optional[str] = Query(None, description="date|code|status|invoice_date|invoice_number|ar_status"),
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
    )
    today = date.today()
    stmt = exclude_voided_invoices(select(Invoice).order_by(Invoice.id.desc()))
    if due_within_days is not None and not overdue_only:
        stmt = stmt.where(
            and_(
                Invoice.due_date.is_not(None),
                Invoice.due_date >= today,
                Invoice.due_date <= (today + timedelta(days=int(due_within_days))),
            )
        )
    rows = list(db.scalars(stmt).all())
    enriched = [enrich_outstanding_invoice(db, r, hide_po=hide_po) for r in rows]
    if overdue_only:
        enriched = [r for r in enriched if (r.get("ar_status") or "") == "overdue"]
    elif due_within_days is not None:
        enriched = [r for r in enriched if (r.get("ar_status") or "") != "closed"]
    enriched = filter_outstanding_rows(
        enriched,
        ar_status=ar_status,
        open_only=open_only,
        customer_id=customer_id,
        q=q,
    )
    enriched = sort_mapped_rows(
        enriched,
        sortable={
            "date": "invoice_date",
            "invoice_date": "invoice_date",
            "code": "invoice_number",
            "invoice_number": "invoice_number",
            "status": "ar_status",
            "ar_status": "ar_status",
            "payment_status": "payment_status",
            "id": "id",
        },
        sort_by=params.sort_by,
        sort_dir=params.sort_dir,
    )
    total = len(enriched)
    page_items = enriched[params.offset : params.offset + params.limit]
    return page_dict(items=page_items, total=total, params=params)


@router.post("/invoice/backfill-fks")
def backfill_invoice_fks(
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> dict:
    """Backfill customer_id and po_id for existing invoices based on delivery chain."""
    updated = 0
    skipped = 0

    invoices = db.query(Invoice).filter(
        (Invoice.customer_id.is_(None)) | (Invoice.po_id.is_(None))
    ).all()

    for inv in invoices:
        changed = False

        if inv.delivery_id and inv.customer_id is None:
            delivery = db.get(DeliveryHeader, inv.delivery_id)
            if delivery and delivery.customer_id:
                inv.customer_id = delivery.customer_id
                changed = True

        if inv.delivery_id and inv.po_id is None:
            resolved = po_id_from_delivery(db, int(inv.delivery_id))
            if resolved:
                inv.po_id = resolved
                changed = True

        if changed:
            updated += 1
        else:
            skipped += 1
    
    db.commit()
    return {
        "updated": updated,
        "skipped": skipped,
        "message": f"Updated {updated} invoices, skipped {skipped} (no FK chain found)"
    }


@router.get("/invoice/{invoice_id}", response_model=InvoiceOut)
def get_invoice(
    invoice_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> Invoice:
    from app.services.delivery_auto_invoice import sync_invoice_lines_from_delivery

    row = db.get(Invoice, invoice_id)
    if not row:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
    sync_invoice_lines_from_delivery(db, int(invoice_id), force=False)
    db.commit()
    db.refresh(row)
    return row


@router.put("/invoice/{invoice_id}", response_model=InvoiceOut)
def update_invoice(
    invoice_id: int,
    body: InvoiceUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "finance")),
) -> Invoice:
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
    # Jika payment/CN diubah, sesuaikan payment_status dari saldo
    if any(
        f in body.model_dump(exclude_unset=True)
        for f in ("payment_amount", "payment_date", "payment_status", "credit_note_amount", "oia_export_usd", "total_amount")
    ):
        if "payment_status" not in body.model_dump(exclude_unset=True):
            sync_payment_status_from_balance(row)
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
    return row


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
        .where(Invoice.due_date.is_not(None), Invoice.voided_at.is_(None))
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
        if invoice_balance(inv) <= 0 or (inv.payment_status or "").lower() == "paid":
            skipped += 1
            continue
        if invoice_ar_status(inv, today=today) == "closed":
            skipped += 1
            continue
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
                f"Generated at: {app_now().isoformat()}Z",
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

@router.get("/invoice/{invoice_id}/details", response_model=list[InvoiceDetailOut])
def list_invoice_details(
    invoice_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> list[InvoiceDetail]:
    from app.services.delivery_auto_invoice import sync_invoice_lines_from_delivery

    if not db.get(Invoice, invoice_id):
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
    sync_invoice_lines_from_delivery(db, int(invoice_id), force=False)
    db.commit()
    rows = db.scalars(
        select(InvoiceDetail)
        .where(InvoiceDetail.invoice_id == invoice_id)
        .order_by(InvoiceDetail.id.asc())
    ).all()
    return rows


@router.post("/invoice/{invoice_id}/details", response_model=InvoiceDetailOut)
def add_invoice_detail(
    invoice_id: int,
    body: InvoiceDetailCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "finance")),
) -> InvoiceDetail:
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
    return row
