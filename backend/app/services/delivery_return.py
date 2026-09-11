"""Retur barang per baris delivery → credit note invoice (outstanding AR)."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    DeliveryDetail,
    DeliveryHeader,
    Invoice,
    InvoiceDetail,
    PoDetail,
    ProductionDetail,
)
from app.timeutil import app_now


def _dec(v: Decimal | None) -> Decimal:
    return v if v is not None else Decimal(0)


def resolve_po_detail_for_delivery_line(db: Session, dd: DeliveryDetail) -> PoDetail | None:
    if dd.po_detail_id:
        return db.get(PoDetail, int(dd.po_detail_id))
    if dd.production_detail_id:
        pd = db.get(ProductionDetail, int(dd.production_detail_id))
        if pd and pd.po_detail_id:
            return db.get(PoDetail, int(pd.po_detail_id))
    return None


def _invoice_for_delivery(db: Session, delivery_id: int) -> Invoice | None:
    return db.scalars(
        select(Invoice).where(Invoice.delivery_id == int(delivery_id)).order_by(Invoice.id.desc()).limit(1)
    ).first()


def _matched_invoice_detail(db: Session, inv: Invoice, dd: DeliveryDetail) -> InvoiceDetail | None:
    """Match by ordinal position within the same delivery (legacy INVPL/SJ convention)."""
    details = list(
        db.scalars(
            select(DeliveryDetail)
            .where(DeliveryDetail.delivery_id == dd.delivery_id)
            .order_by(DeliveryDetail.id.asc())
        ).all()
    )
    idx = next((i for i, row in enumerate(details) if int(row.id) == int(dd.id)), None)
    if idx is None:
        return None
    inv_details = list(
        db.scalars(
            select(InvoiceDetail)
            .where(InvoiceDetail.invoice_id == inv.id)
            .order_by(InvoiceDetail.id.asc())
        ).all()
    )
    if idx >= len(inv_details):
        return None
    return inv_details[idx]


def apply_delivery_line_return(
    db: Session,
    *,
    detail_id: int,
    qty: Decimal,
    remark: str | None = None,
    actor: str | None = None,
) -> dict[str, Any]:
    """Catat retur qty pada baris SJ; tambah credit_note_amount pada invoice terkait."""
    dd = db.get(DeliveryDetail, int(detail_id))
    if not dd or not dd.delivery_id:
        raise HTTPException(status_code=404, detail="Baris delivery tidak ditemukan")
    dh = db.get(DeliveryHeader, int(dd.delivery_id))
    if not dh:
        raise HTTPException(status_code=404, detail="Delivery tidak ditemukan")

    status = (dh.status or "").lower()
    if status not in ("sent", "delivered", "completed"):
        # Izinkan juga jika sudah ada invoice (kadang status masih draft di data lama)
        inv_probe = _invoice_for_delivery(db, int(dh.id))
        if not inv_probe:
            raise HTTPException(
                status_code=400,
                detail="Retur hanya untuk delivery yang sudah dikirim / punya invoice",
            )

    shipped = _dec(dd.qty)
    already = _dec(dd.returned_qty)
    remaining = shipped - already
    if qty <= 0:
        raise HTTPException(status_code=400, detail="Qty retur harus > 0")
    if qty > remaining:
        raise HTTPException(
            status_code=400,
            detail=f"Qty retur ({qty}) melebihi sisa yang bisa diretur ({remaining})",
        )

    inv = _invoice_for_delivery(db, int(dh.id))
    if not inv:
        raise HTTPException(
            status_code=400,
            detail="Belum ada invoice untuk delivery ini — buat invoice dulu sebelum retur",
        )

    pod = resolve_po_detail_for_delivery_line(db, dd)
    invd = _matched_invoice_detail(db, inv, dd)
    unit_price: Decimal | None = None
    if invd is not None and invd.unit_price is not None:
        unit_price = _dec(invd.unit_price)
    elif pod is not None and pod.unit_price is not None:
        unit_price = _dec(pod.unit_price)
    if unit_price is None:
        raise HTTPException(
            status_code=400,
            detail="Harga satuan tidak ditemukan untuk baris ini (PO/invoice)",
        )

    credit = (qty * unit_price).quantize(Decimal("0.01"))
    dd.returned_qty = already + qty

    if invd is not None:
        # Sesuaikan baris invoice bila ada (audit qty faktur)
        new_qty = max(_dec(invd.qty) - qty, Decimal(0))
        invd.qty = new_qty
        if invd.unit_price is not None:
            invd.amount = (new_qty * _dec(invd.unit_price)).quantize(Decimal("0.01"))
        note = (remark or "").strip()
        if note:
            prev = (invd.remark or "").strip()
            invd.remark = f"{prev} | RETUR {qty}" if prev else f"RETUR {qty}: {note}"
        elif not (invd.remark or "").strip():
            invd.remark = f"RETUR {qty}"

    inv.credit_note_amount = _dec(inv.credit_note_amount) + credit
    if not inv.credit_note_date:
        inv.credit_note_date = app_now().date()
    if not (inv.credit_note_no or "").strip():
        base = (inv.invoice_number or f"INV-{inv.id}").strip()
        inv.credit_note_no = f"CN-{base}"

    return {
        "delivery_detail_id": int(dd.id),
        "delivery_id": int(dh.id),
        "invoice_id": int(inv.id),
        "invoice_number": inv.invoice_number,
        "returned_qty": float(dd.returned_qty or 0),
        "return_qty_this": float(qty),
        "unit_price": float(unit_price),
        "credit_amount": float(credit),
        "credit_note_amount": float(inv.credit_note_amount or 0),
        "remaining_returnable": float(shipped - _dec(dd.returned_qty)),
        "actor": actor,
        "remark": (remark or "").strip() or None,
    }
