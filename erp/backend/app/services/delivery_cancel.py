"""Soft-delete delivery (flag is_deleted). Qty kembali tersedia; dokumen tetap di DB."""

from __future__ import annotations

from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DeliveryHeader, Invoice, PoHeader
from app.services.audit import log_change
from app.services.business_rules import po_ids_from_delivery
from app.services.delivery_active import delivery_header_is_deleted
from app.services.mkt_workflow import reconcile_po_stage_after_delivery_cancel
from app.services.notifications import create_notification_for_roles
from app.timeutil import app_now

_SENT = frozenset({"sent", "delivered", "completed"})
_VOID_ROLES = frozenset({"admin", "finance"})


def _dec(value) -> Decimal:
    if value is None:
        return Decimal(0)
    return Decimal(str(value))


def _is_sent(status: str | None) -> bool:
    return (status or "").strip().lower() in _SENT


def _invoice_for_delivery(db: Session, delivery_id: int) -> Invoice | None:
    return db.scalars(
        select(Invoice).where(Invoice.delivery_id == int(delivery_id)).limit(1)
    ).first()


def _invoice_is_open(inv: Invoice) -> bool:
    return getattr(inv, "voided_at", None) is None


def _invoice_is_paid(inv: Invoice) -> bool:
    if (inv.payment_status or "").strip().lower() == "paid":
        return True
    return _dec(inv.payment_amount) > 0


def _invoice_has_credit_note(inv: Invoice) -> bool:
    if (inv.credit_note_no or "").strip():
        return True
    return _dec(inv.credit_note_amount) > 0


def _delivery_has_bc(row: DeliveryHeader) -> bool:
    if (row.bc_number or "").strip():
        return True
    if row.bc_date is not None:
        return True
    return bool(row.customs_declaration_id)


def soft_delete_delivery(
    db: Session,
    delivery_id: int,
    *,
    reason: str,
    actor: str,
    role: str | None,
) -> DeliveryHeader:
    text = (reason or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Alasan hapus wajib diisi")

    row = db.get(DeliveryHeader, int(delivery_id))
    if not row:
        raise HTTPException(status_code=404, detail="Delivery tidak ditemukan")
    if delivery_header_is_deleted(row):
        raise HTTPException(status_code=400, detail="Delivery sudah dihapus")
    if _is_sent(row.status):
        raise HTTPException(
            status_code=400,
            detail="Surat jalan sudah terkirim. Gunakan retur, jangan hapus.",
        )
    if _delivery_has_bc(row):
        raise HTTPException(
            status_code=400,
            detail="Delivery sudah punya dokumen BC. Gunakan retur, jangan hapus surat jalan.",
        )

    inv = _invoice_for_delivery(db, int(row.id))
    open_invoice = inv if inv is not None and _invoice_is_open(inv) else None
    if open_invoice is not None:
        if _invoice_is_paid(open_invoice) or _invoice_has_credit_note(open_invoice):
            raise HTTPException(
                status_code=400,
                detail="Invoice sudah dibayar atau punya credit note. Gunakan retur.",
            )
        if (role or "").strip().lower() not in _VOID_ROLES:
            raise HTTPException(
                status_code=403,
                detail="Invoice belum dibayar hanya boleh dihapus oleh admin atau finance",
            )
        open_invoice.voided_at = app_now()
        open_invoice.void_reason = text
        log_change(
            db,
            entity_type="invoice",
            entity_id=int(open_invoice.id),
            action="void",
            before={"voided_at": None, "payment_status": open_invoice.payment_status},
            after={"voided_at": open_invoice.voided_at.isoformat(), "void_reason": text},
            actor=actor,
        )

    prev_status = row.status
    now = app_now()
    row.is_deleted = True
    row.deleted_at = now
    row.deleted_by = actor
    row.delete_reason = text
    # Mirror legacy cancel columns for older readers; status tetap draft.
    row.cancel_reason = text
    row.cancelled_at = now
    row.cancelled_by = actor
    log_change(
        db,
        entity_type="delivery",
        entity_id=int(row.id),
        action="delete",
        before={"status": prev_status, "is_deleted": False},
        after={
            "status": prev_status,
            "is_deleted": True,
            "delete_reason": text,
            "deleted_by": actor,
            "invoice_id": int(open_invoice.id) if open_invoice is not None else None,
        },
        actor=actor,
    )
    create_notification_for_roles(
        db,
        ("admin", "marketing", "warehouse", "finance"),
        title=f"Delivery {row.delivery_number or row.id} dihapus",
        message=f"Surat jalan dihapus (soft-delete). Alasan: {text}",
        category="delivery",
        entity_type="delivery",
        entity_id=row.id,
        route_path="/admin/delivery",
        route_query={"delivery_id": row.id},
    )

    db.flush()
    for po_id in po_ids_from_delivery(db, int(row.id)):
        po = db.get(PoHeader, int(po_id))
        if po is None:
            continue
        reconcile_po_stage_after_delivery_cancel(
            db,
            po,
            actor=actor,
            exclude_delivery_id=int(row.id),
        )

    db.commit()
    db.refresh(row)
    return row


def cancel_delivery(
    db: Session,
    delivery_id: int,
    *,
    reason: str,
    actor: str,
    role: str | None,
) -> DeliveryHeader:
    """Alias lama → soft-delete (kompatibilitas client/route cancel)."""
    return soft_delete_delivery(
        db,
        delivery_id,
        reason=reason,
        actor=actor,
        role=role,
    )
