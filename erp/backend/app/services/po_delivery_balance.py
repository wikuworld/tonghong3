"""Saldo qty order PO vs qty terkirim (modul delivery)."""

from __future__ import annotations

from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import DeliveryDetail, DeliveryHeader, PoDetail, ProductionDetail

# Toleransi ukur kecil: max(2 SF, 0.5% qty order). Izinkan overship otomatis dalam batas ini.
OVERSHIP_ABS_SF = Decimal("2")
OVERSHIP_PCT = Decimal("0.005")


def _net_delivered_qty_expr():
    return DeliveryDetail.qty - func.coalesce(DeliveryDetail.returned_qty, 0)


def _delivery_not_cancelled():
    status = func.lower(func.trim(func.coalesce(DeliveryHeader.status, "")))
    return status.notin_(("cancelled", "canceled"))


def _dec_qty(v: Decimal | float | int | None) -> Decimal:
    if v is None:
        return Decimal(0)
    return Decimal(str(v))


def overship_allowance(order_qty: Decimal | float | int | None) -> Decimal:
    """Batas overship otomatis terhadap saldo order (SF)."""
    order = _dec_qty(order_qty)
    if order <= 0:
        return OVERSHIP_ABS_SF
    pct = (order * OVERSHIP_PCT).quantize(Decimal("0.01"))
    return max(OVERSHIP_ABS_SF, pct)


def within_overship_tolerance(
    qty: Decimal | float | int | None,
    remaining: Decimal | float | int | None,
    *,
    order_qty: Decimal | float | int | None = None,
) -> bool:
    """True jika qty > remaining tetapi selisih masih dalam toleransi ukur."""
    q = _dec_qty(qty)
    rem = _dec_qty(remaining)
    if q <= rem:
        return True
    overage = q - rem
    base = order_qty if order_qty is not None else rem
    return overage <= overship_allowance(base) + Decimal("0.0000001")


def sum_delivered_qty_for_po_detail(
    db: Session,
    po_detail_id: int,
    *,
    exclude_delivery_detail_id: int | None = None,
) -> Decimal:
    """Jumlah qty delivery NET (qty − retur) untuk baris PO."""
    via_production = (
        select(func.coalesce(func.sum(_net_delivered_qty_expr()), 0))
        .select_from(DeliveryDetail)
        .join(ProductionDetail, DeliveryDetail.production_detail_id == ProductionDetail.id)
        .join(DeliveryHeader, DeliveryHeader.id == DeliveryDetail.delivery_id)
        .where(ProductionDetail.po_detail_id == po_detail_id, _delivery_not_cancelled())
    )
    if exclude_delivery_detail_id is not None:
        via_production = via_production.where(DeliveryDetail.id != exclude_delivery_detail_id)
    total_prod = db.scalars(via_production).one()

    via_direct = (
        select(func.coalesce(func.sum(_net_delivered_qty_expr()), 0))
        .select_from(DeliveryDetail)
        .join(DeliveryHeader, DeliveryHeader.id == DeliveryDetail.delivery_id)
        .where(
            DeliveryDetail.po_detail_id == po_detail_id,
            or_(
                DeliveryDetail.production_detail_id.is_(None),
                DeliveryDetail.production_detail_id == 0,
            ),
            _delivery_not_cancelled(),
        )
    )
    if exclude_delivery_detail_id is not None:
        via_direct = via_direct.where(DeliveryDetail.id != exclude_delivery_detail_id)
    total_direct = db.scalars(via_direct).one()

    return Decimal(total_prod or 0) + Decimal(total_direct or 0)


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
    production_detail_id: int | None = None,
    po_detail_id: int | None = None,
    qty: Decimal | None,
    exclude_delivery_detail_id: int | None = None,
) -> None:
    """Tolak kiriman yang melebihi saldo order di luar toleransi ukur kecil."""
    if qty is None or qty <= 0:
        return
    resolved_po_detail_id = po_detail_id
    if resolved_po_detail_id is None and production_detail_id is not None:
        pd = db.get(ProductionDetail, production_detail_id)
        if not pd or pd.po_detail_id is None:
            return
        resolved_po_detail_id = int(pd.po_detail_id)
    if resolved_po_detail_id is None:
        return
    pod = db.get(PoDetail, int(resolved_po_detail_id))
    remaining = remaining_po_detail_qty(
        db, int(resolved_po_detail_id), exclude_delivery_detail_id=exclude_delivery_detail_id
    )
    if remaining is None:
        return
    q = _dec_qty(qty)
    if q <= remaining:
        return
    order_qty = pod.quantity_order if pod else remaining
    if within_overship_tolerance(q, remaining, order_qty=order_qty):
        return
    allow = overship_allowance(order_qty)
    raise HTTPException(
        status_code=400,
        detail=(
            f"Qty kirim ({q}) melebihi saldo order ({remaining} SF) "
            f"di luar toleransi ukur ({allow} SF). "
            "Revisi PO/marketing jika perlu menambah qty order."
        ),
    )


def sync_po_detail_balance_qty(db: Session, po_detail_id: int) -> Decimal | None:
    """Update kolom denormalized po_details.balance_qty = order − delivered."""
    pod = db.get(PoDetail, po_detail_id)
    if not pod or pod.quantity_order is None:
        return None
    delivered = sum_delivered_qty_for_po_detail(db, po_detail_id)
    bal = pod.quantity_order - delivered
    if bal < 0:
        bal = Decimal("0")
    pod.balance_qty = bal
    return bal


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
                f"Total rencana kirim ({total}) melebihi qty order ({order_qty}) "
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
