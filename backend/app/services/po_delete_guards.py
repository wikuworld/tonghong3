"""Validasi sebelum menghapus header PO."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import HTTPException
from sqlalchemy import select

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def validate_po_deletable(db: "Session", po_id: int) -> None:
    """Raise HTTPException jika PO tidak boleh dihapus."""
    from app.models import (
        DeliveryDetail,
        DeliveryHeader,
        Invoice,
        PpicsAssignment,
        PoDetail,
        ProductionDetail,
        ProductionOrder,
        SubconInvoice,
    )

    active_invoices = db.query(SubconInvoice).filter(
        SubconInvoice.po_id == po_id,
        SubconInvoice.status.notin_(["cancelled", "paid"]),
    ).count()
    if active_invoices > 0:
        raise HTTPException(
            status_code=400,
            detail="Tidak dapat menghapus PO dengan subcon invoice yang aktif.",
        )

    active_assignments = db.query(PpicsAssignment).filter(
        PpicsAssignment.po_id == po_id,
        PpicsAssignment.status.notin_(["completed", "cancelled"]),
    ).count()
    if active_assignments > 0:
        raise HTTPException(
            status_code=400,
            detail="Tidak dapat menghapus PO dengan PPIC assignment yang aktif.",
        )

    production = db.scalars(
        select(ProductionOrder.id).where(ProductionOrder.po_id == po_id).limit(1)
    ).first()
    if production is not None:
        raise HTTPException(
            status_code=400,
            detail="Tidak dapat menghapus PO yang sudah memiliki data production.",
        )

    invoice = db.scalars(select(Invoice.id).where(Invoice.po_id == po_id).limit(1)).first()
    if invoice is not None:
        raise HTTPException(
            status_code=400,
            detail="Tidak dapat menghapus PO yang sudah memiliki invoice.",
        )

    delivery = db.scalars(
        select(DeliveryHeader.id)
        .join(DeliveryDetail, DeliveryDetail.delivery_id == DeliveryHeader.id)
        .join(ProductionDetail, ProductionDetail.id == DeliveryDetail.production_detail_id)
        .join(PoDetail, PoDetail.id == ProductionDetail.po_detail_id)
        .where(PoDetail.po_id == po_id)
        .limit(1)
    ).first()
    if delivery is not None:
        raise HTTPException(
            status_code=400,
            detail="Tidak dapat menghapus PO yang sudah memiliki delivery.",
        )
