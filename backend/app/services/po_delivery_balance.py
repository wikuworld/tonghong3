"""Saldo qty order PO vs qty terkirim (modul delivery)."""

from __future__ import annotations

from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import DeliveryDetail, PoDetail, ProductionDetail


def sum_delivered_qty_for_po_detail(
    db: Session,
    po_detail_id: int,
    *,
    exclude_delivery_detail_id: int | None = None,
) -> Decimal:
    stmt = (
        select(func.coalesce(func.sum(DeliveryDetail.qty), 0))
        .select_from(DeliveryDetail)
        .join(ProductionDetail, DeliveryDetail.production_detail_id == ProductionDetail.id)
        .where(ProductionDetail.po_detail_id == po_detail_id)
    )
    if exclude_delivery_detail_id is not None:
        stmt = stmt.where(DeliveryDetail.id != exclude_delivery_detail_id)
    total = db.scalars(stmt).one()
    return Decimal(total or 0)


def remaining_po_detail_qty(
    db: Session,
    po_detail_id: int,
    *,
    exclude_delivery_detail_id: int | None = None,
) -> Decimal | None:
    pod = db.get(PoDetail, po_detail_id)
    if not pod or pod.quantity_order is None:
        return None
    delivered = sum_delivered_qty_for_po_detail(
        db, po_detail_id, exclude_delivery_detail_id=exclude_delivery_detail_id
    )
    return pod.quantity_order - delivered


def validate_delivery_qty_against_po_balance(
    db: Session,
    *,
    production_detail_id: int,
    qty: Decimal | None,
    exclude_delivery_detail_id: int | None = None,
) -> None:
    """Tolak kiriman yang melebihi saldo order PO (qty_order − terkirim)."""
    if qty is None or qty <= 0:
        return
    pd = db.get(ProductionDetail, production_detail_id)
    if not pd or pd.po_detail_id is None:
        return
    remaining = remaining_po_detail_qty(
        db, int(pd.po_detail_id), exclude_delivery_detail_id=exclude_delivery_detail_id
    )
    if remaining is None:
        return
    if qty > remaining:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Qty kirim ({qty}) melebihi saldo order ({remaining} SF). "
                "Revisi PO/marketing jika perlu menambah qty order."
            ),
        )


def _dec_qty(v: Decimal | float | int | None) -> Decimal:
    if v is None:
        return Decimal(0)
    return Decimal(str(v))


def schedule_qty_total(schedules: list) -> Decimal:
    """Jumlah qty dari list jadwal (objek dengan atribut/qty key `qty`)."""
    total = Decimal(0)
    for item in schedules:
        if isinstance(item, dict):
            total += _dec_qty(item.get("qty"))
        else:
            total += _dec_qty(getattr(item, "qty", None))
    return total


def validate_schedule_total_against_order(
    db: Session,
    po_detail_id: int,
    schedules: list,
) -> None:
    """Tolak jika total qty jadwal kirim > quantity_order baris PO."""
    pod = db.get(PoDetail, po_detail_id)
    if not pod or pod.quantity_order is None:
        return
    order_qty = _dec_qty(pod.quantity_order)
    total = schedule_qty_total(schedules)
    if total > order_qty:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Total jadwal kirim ({total}) melebihi qty order ({order_qty}) "
                f"untuk baris PO #{po_detail_id}. Kurangi qty slot atau naikkan qty order."
            ),
        )


def remaining_schedule_qty(db: Session, po_detail_id: int, existing_schedules: list | None = None) -> Decimal:
    """Sisa qty yang masih boleh dijadwalkan (order − sum jadwal existing)."""
    pod = db.get(PoDetail, po_detail_id)
    if not pod or pod.quantity_order is None:
        return Decimal(0)
    order_qty = _dec_qty(pod.quantity_order)
    if existing_schedules is None:
        from app.models import PoDetailDelivery

        existing_schedules = list(
            db.scalars(
                select(PoDetailDelivery)
                .where(PoDetailDelivery.po_detail_id == po_detail_id)
                .order_by(PoDetailDelivery.sequence_no.asc())
            ).all()
        )
    used = schedule_qty_total(existing_schedules)
    rem = order_qty - used
    return rem if rem > 0 else Decimal(0)
