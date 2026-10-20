"""Buat Invoice otomatis (nomor THIN) saat Surat Jalan dibuat."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import select

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.models import Invoice


def _dec(v) -> Decimal:
    if v is None:
        return Decimal("0")
    if isinstance(v, Decimal):
        return v
    return Decimal(str(v))


def sync_invoice_lines_from_delivery(
    db: "Session",
    invoice_id: int,
    *,
    force: bool = False,
) -> int:
    """Isi invoice_details + total dari baris delivery. Return jumlah baris.

    Default tidak menimpa bila sudah ada baris (kecuali force=True).
    """
    from app.models import (
        DeliveryDetail,
        Invoice,
        InvoiceDetail,
        PackingDetail,
        PackingHeader,
        PoDetail,
        ProductionDetail,
    )
    from app.services.marketing_documents import _item_description

    inv = db.get(Invoice, int(invoice_id))
    if not inv or not inv.delivery_id:
        return 0

    existing = list(
        db.scalars(select(InvoiceDetail).where(InvoiceDetail.invoice_id == int(invoice_id))).all()
    )
    if existing and not force:
        # Pastikan total terisi bila baris ada tapi total kosong
        if inv.total_amount is None:
            total = sum((_dec(x.amount) for x in existing), Decimal("0"))
            inv.total_amount = total
            if not (inv.total_in_words or "").strip():
                from app.services.marketing_documents import usd_amount_in_words

                inv.total_in_words = usd_amount_in_words(total)
        return len(existing)

    if existing and force:
        for row in existing:
            db.delete(row)
        db.flush()

    details = list(
        db.scalars(
            select(DeliveryDetail)
            .where(DeliveryDetail.delivery_id == int(inv.delivery_id))
            .order_by(DeliveryDetail.id.asc())
        ).all()
    )
    if not details:
        if force:
            inv.total_amount = Decimal("0")
            if not (inv.total_in_words or "").strip():
                from app.services.marketing_documents import usd_amount_in_words

                inv.total_in_words = usd_amount_in_words(Decimal("0"))
        return 0

    total = Decimal("0")
    created = 0
    for dd in details:
        pod: PoDetail | None = None
        if dd.po_detail_id:
            pod = db.get(PoDetail, int(dd.po_detail_id))
        elif dd.production_detail_id:
            pd = db.get(ProductionDetail, int(dd.production_detail_id))
            if pd and pd.po_detail_id:
                pod = db.get(PoDetail, int(pd.po_detail_id))

        qty = _dec(dd.qty)
        unit_price = _dec(pod.unit_price) if pod and pod.unit_price is not None else None
        amount = (qty * unit_price).quantize(Decimal("0.01")) if unit_price is not None else None
        if amount is not None:
            total += amount

        nw = _dec(dd.weight) if dd.weight is not None else None
        roll = int(dd.qty_roll) if dd.qty_roll is not None else None
        pcs = int(dd.qty_pcs) if dd.qty_pcs is not None else None

        # Lengkapi roll/pcs dari packing detail bila kosong
        if (roll is None or pcs is None) and dd.packing_detail_id:
            pkd = db.get(PackingDetail, int(dd.packing_detail_id))
            if pkd:
                if roll is None and pkd.qty_roll is not None:
                    roll = int(pkd.qty_roll)
                if pcs is None and pkd.qty_pcs is not None:
                    pcs = int(pkd.qty_pcs)
                if nw is None and pkd.weight_net is not None:
                    nw = _dec(pkd.weight_net)

        desc = _item_description(pod) if pod else "—"
        color = (pod.color or "").strip() if pod else None
        db.add(
            InvoiceDetail(
                invoice_id=int(invoice_id),
                item_description=desc[:255] if desc else None,
                color=color[:100] if color else None,
                qty=qty if qty else None,
                unit_price=unit_price,
                amount=amount,
                roll=roll,
                pcs=pcs,
                net_weight=nw,
            )
        )
        created += 1

    inv.total_amount = total
    if not (inv.packing_list_number or "").strip() and inv.delivery_id:
        from app.models import DeliveryHeader

        dh = db.get(DeliveryHeader, int(inv.delivery_id))
        if dh and dh.packing_id:
            ph = db.get(PackingHeader, int(dh.packing_id))
            if ph and (ph.packing_number or "").strip():
                inv.packing_list_number = ph.packing_number.strip()[:100]
    if not (inv.total_in_words or "").strip():
        from app.services.marketing_documents import usd_amount_in_words

        inv.total_in_words = usd_amount_in_words(total)
    db.flush()
    return created


def ensure_invoice_for_delivery(
    db: "Session",
    delivery_id: int,
    *,
    actor: str | None = None,
    allow_draft: bool = True,
) -> "Invoice | None":
    """Idempotent: return invoice existing, atau buat baru dengan nomor THIN.

    Return None jika delivery belum punya detail (belum siap di-invoice).
    """
    from app.models import Customer, DeliveryDetail, DeliveryHeader, Invoice, PoHeader
    from app.services.audit import log_change
    from app.services.business_rules import (
        joined_po_numbers_for_delivery,
        po_id_from_delivery,
        validate_invoice_against_delivery,
    )
    from app.services.document_numbers import allocate_invoice_number
    from app.services.mkt_workflow import sync_invoice_billing_from_delivery
    from app.services.notifications import create_notification_for_roles

    existing = db.scalars(
        select(Invoice).where(Invoice.delivery_id == int(delivery_id)).limit(1)
    ).first()
    if existing:
        if getattr(existing, "voided_at", None) is not None:
            return existing
        sync_invoice_lines_from_delivery(db, int(existing.id), force=False)
        return existing

    hdr = db.get(DeliveryHeader, int(delivery_id))
    if hdr and (
        bool(getattr(hdr, "is_deleted", False))
        or (hdr.status or "").strip().lower() in ("cancelled", "canceled")
    ):
        return None

    details = db.scalars(
        select(DeliveryDetail).where(DeliveryDetail.delivery_id == int(delivery_id))
    ).all()
    if not details:
        return None

    validate_invoice_against_delivery(
        db,
        int(delivery_id),
        None,
        allow_draft=allow_draft,
        skip_if_exists=False,
    )

    delivery = db.get(DeliveryHeader, int(delivery_id))
    if not delivery:
        return None

    po_id = po_id_from_delivery(db, int(delivery_id))
    po_for_num: PoHeader | None = db.get(PoHeader, int(po_id)) if po_id else None
    inv_date = delivery.delivery_date
    invoice_number = allocate_invoice_number(db, po=po_for_num, on_date=inv_date)
    po_number = joined_po_numbers_for_delivery(db, int(delivery_id)) or None

    customer_name = None
    customer_address = None
    customer_phone = None
    if delivery.customer_id:
        cust = db.get(Customer, int(delivery.customer_id))
        if cust:
            customer_name = cust.name
            customer_address = cust.address
            customer_phone = cust.phone

    row = Invoice(
        delivery_id=int(delivery_id),
        customer_id=delivery.customer_id,
        po_id=int(po_id) if po_id else None,
        invoice_number=invoice_number,
        po_number=po_number,
        customer_name=customer_name,
        customer_address=customer_address,
        customer_phone=customer_phone,
        invoice_date=inv_date,
        payment_status="unpaid",
    )
    db.add(row)
    db.flush()
    sync_invoice_lines_from_delivery(db, int(row.id), force=True)
    log_change(
        db,
        entity_type="invoice",
        entity_id=row.id,
        action="create_auto_from_delivery",
        after={
            "invoice_number": row.invoice_number,
            "delivery_id": row.delivery_id,
            "customer_id": row.customer_id,
            "po_id": row.po_id,
            "total_amount": float(row.total_amount) if row.total_amount is not None else None,
        },
        actor=actor or "system",
    )
    try:
        create_notification_for_roles(
            db,
            ("admin", "finance", "marketing"),
            title=f"Invoice {row.invoice_number or row.id} dibuat otomatis",
            message=f"Otomatis dari surat jalan ID {row.delivery_id}",
            category="invoice",
            entity_type="invoice",
            entity_id=row.id,
            route_path="/admin/invoice",
            route_query={"invoice_id": row.id},
        )
    except Exception:
        pass
    sync_invoice_billing_from_delivery(db, int(delivery_id))
    return row
