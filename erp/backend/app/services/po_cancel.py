"""Batal sales order: status tetap di ERP, MRP ditandai cancelled bila sudah tersinkron."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    DeliveryDetail,
    DeliveryHeader,
    Invoice,
    PpicsAssignment,
    PoDetail,
    PoHeader,
    ProductionDetail,
)
from app.services.audit import log_change
from app.services.delivery_active import delivery_header_is_active_clause
from app.services.mrp_po_alloc import MrpAllocUnreachable, require_mrp_alloc_snapshot
from app.services.mrp_po_sync import sync_po_details_to_mrp
from app.services.notifications import create_notification_for_roles
from app.timeutil import app_now

_SYNCED_STATUSES = frozenset({"confirmed", "production", "completed"})
_CANCELLED_STATUSES = frozenset({"cancelled"})


def _dec(value: Any) -> Decimal:
    if value is None or value == "":
        return Decimal(0)
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal(0)


def _detail_ids(db: Session, po_id: int) -> list[int]:
    return [
        int(x)
        for x in db.scalars(select(PoDetail.id).where(PoDetail.po_id == po_id)).all()
        if x is not None
    ]


def _active_delivery_id(db: Session, po_id: int) -> int | None:
    found = db.scalars(
        select(DeliveryHeader.id)
        .join(DeliveryDetail, DeliveryDetail.delivery_id == DeliveryHeader.id)
        .join(ProductionDetail, ProductionDetail.id == DeliveryDetail.production_detail_id)
        .join(PoDetail, PoDetail.id == ProductionDetail.po_detail_id)
        .where(PoDetail.po_id == po_id, delivery_header_is_active_clause())
        .limit(1)
    ).first()
    return int(found) if found is not None else None


def _open_invoice_id(db: Session, po_id: int) -> int | None:
    found = db.scalars(
        select(Invoice.id)
        .where(Invoice.po_id == po_id, Invoice.voided_at.is_(None))
        .limit(1)
    ).first()
    return int(found) if found is not None else None


def _production_detail_id(db: Session, po_id: int) -> int | None:
    found = db.scalars(
        select(ProductionDetail.id)
        .join(PoDetail, PoDetail.id == ProductionDetail.po_detail_id)
        .where(PoDetail.po_id == po_id)
        .limit(1)
    ).first()
    return int(found) if found is not None else None


def _ppic_in_progress_id(db: Session, po_id: int) -> int | None:
    found = db.scalars(
        select(PpicsAssignment.id)
        .where(PpicsAssignment.po_id == po_id, PpicsAssignment.status == "in_progress")
        .limit(1)
    ).first()
    return int(found) if found is not None else None


def _pending_ppic(db: Session, po_id: int) -> list[PpicsAssignment]:
    return list(
        db.scalars(
            select(PpicsAssignment).where(
                PpicsAssignment.po_id == po_id,
                PpicsAssignment.status == "pending",
            )
        ).all()
    )


def _alloc_has_work(alloc: dict[int, dict[str, str]]) -> bool:
    for row in alloc.values():
        if _dec(row.get("mrp_qty_processed")) > 0 or _dec(row.get("mrp_qty_wip")) > 0:
            return True
    return False


def _mrp_push_needed(detail_ids: list[int], alloc: dict[int, dict[str, str]]) -> bool:
    """Push bila ada baris yang belum cancelled di MRP, atau MRP belum punya barisnya."""
    if not detail_ids:
        return False
    for detail_id in detail_ids:
        row = alloc.get(int(detail_id))
        if row is None:
            return True
        if (row.get("mrp_alloc_status") or "") != "cancelled":
            return True
    return False


def cancel_sales_order(
    db: Session,
    po_id: int,
    *,
    reason: str,
    actor: str,
) -> PoHeader:
    text = (reason or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Alasan batal wajib diisi")

    row = db.get(PoHeader, int(po_id))
    if not row:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")
    status = (row.status or "").strip().lower()
    if status in _CANCELLED_STATUSES:
        return row

    if _active_delivery_id(db, int(row.id)) is not None:
        raise HTTPException(
            status_code=400,
            detail="SO sudah punya surat jalan aktif. Selesaikan atau hapus surat jalan dulu.",
        )
    if _open_invoice_id(db, int(row.id)) is not None:
        raise HTTPException(
            status_code=400,
            detail="SO sudah punya invoice yang belum void.",
        )
    if _production_detail_id(db, int(row.id)) is not None:
        raise HTTPException(
            status_code=400,
            detail="SO sudah masuk produksi. Batal tidak melepas hasil produksi.",
        )
    if _ppic_in_progress_id(db, int(row.id)) is not None:
        raise HTTPException(
            status_code=400,
            detail="Assignment PPIC masih dikerjakan. Selesaikan atau lepas dulu.",
        )

    detail_ids = _detail_ids(db, int(row.id))
    need_push = False
    if status in _SYNCED_STATUSES:
        try:
            alloc = require_mrp_alloc_snapshot(detail_ids)
        except MrpAllocUnreachable as exc:
            raise HTTPException(
                status_code=400,
                detail="MRP tidak terjangkau. SO tidak dibatalkan.",
            ) from exc
        if _alloc_has_work(alloc):
            raise HTTPException(
                status_code=400,
                detail="SO sudah masuk rencana atau WIP MRP. Batal tidak melepas rencana yang berjalan.",
            )
        need_push = _mrp_push_needed(detail_ids, alloc)

    prev_status = row.status
    now = app_now()
    row.status = "cancelled"
    row.cancel_reason = text
    row.cancelled_at = now
    row.cancelled_by = actor
    pending_ids: list[int] = []
    for assignment in _pending_ppic(db, int(row.id)):
        assignment.status = "cancelled"
        pending_ids.append(int(assignment.id))

    log_change(
        db,
        entity_type="sales_order",
        entity_id=int(row.id),
        action="cancel",
        before={"status": prev_status},
        after={
            "status": "cancelled",
            "cancel_reason": text,
            "cancelled_by": actor,
            "ppic_pending_closed": pending_ids,
        },
        actor=actor,
    )
    po_number = (row.po_number or str(row.id)).strip()
    create_notification_for_roles(
        db,
        ("admin", "marketing", "ppic", "finance"),
        title=f"SO {po_number} dibatalkan",
        message=f"Dibatalkan oleh {actor}. Alasan: {text}",
        category="po_status",
        entity_type="sales_order",
        entity_id=int(row.id),
        route_path="/admin/marketing-flow/outstanding",
        route_query={"material_status": "cancelled", "po_q": po_number},
    )
    db.flush()

    if need_push:
        try:
            sync_po_details_to_mrp(db, po_id=int(row.id), raise_on_error=True)
        except Exception as exc:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail="MRP menolak batal. SO di ERP tidak diubah.",
            ) from exc

    db.commit()
    db.refresh(row)
    return row
