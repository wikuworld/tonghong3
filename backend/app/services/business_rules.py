"""Aturan alur: PO → Production → QC → Packing → Delivery → Invoice."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import HTTPException
from sqlalchemy import select

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

# --- PO status ---
_ALLOWED_PO: dict[str, set[str]] = {
    "draft": {"draft", "confirmed"},
    "confirmed": {"confirmed", "production", "completed"},
    "production": {"production", "completed", "confirmed"},
    "completed": {"completed"},
}


def validate_po_status_transition(old: str | None, new: str | None) -> None:
    if new is None:
        return
    o = ((old or "draft").strip() or "draft")
    n = new.strip()
    if o == n:
        return
    allowed = _ALLOWED_PO.get(o, {"draft", "confirmed", "production", "completed"})
    if n not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Transisi status PO tidak valid: {o!r} → {n!r}",
        )


# --- Packing ↔ Production + QC ---
def validate_packing_links(
    db: "Session",
    production_id: int,
    qc_header_id: int,
) -> None:
    from app.models import ProductionOrder, QcHeader

    pr = db.get(ProductionOrder, production_id)
    if not pr:
        raise HTTPException(status_code=400, detail="Production tidak ditemukan")
    qc = db.get(QcHeader, qc_header_id)
    if not qc:
        raise HTTPException(status_code=400, detail="QC header tidak ditemukan")
    if qc.production_id and qc.production_id != production_id:
        raise HTTPException(
            status_code=400,
            detail="QC header harus untuk production_order yang sama",
        )


# --- Delivery ↔ Packing ---
def require_packing_ready(db: "Session", packing_id: int) -> None:
    from app.models import PackingHeader

    p = db.get(PackingHeader, packing_id)
    if not p:
        raise HTTPException(status_code=400, detail="Packing tidak ditemukan")
    if (p.status or "").lower() != "done":
        raise HTTPException(
            status_code=400,
            detail="Packing harus status 'done' sebelum dibuat delivery",
        )


# --- Invoice ↔ Delivery ---
def po_numbers_from_delivery(db: "Session", delivery_id: int) -> set[str]:
    from app.models import DeliveryDetail, PoDetail, PoHeader, ProductionDetail

    details = db.scalars(
        select(DeliveryDetail).where(DeliveryDetail.delivery_id == delivery_id)
    ).all()
    seen: set[str] = set()
    for d in details:
        if not d.production_detail_id:
            continue
        pd = db.get(ProductionDetail, d.production_detail_id)
        if not pd or not pd.po_detail_id:
            continue
        pod = db.get(PoDetail, pd.po_detail_id)
        if not pod:
            continue
        ph = db.get(PoHeader, pod.po_id)
        if ph and ph.po_number:
            seen.add(ph.po_number)
    return seen


def validate_invoice_against_delivery(
    db: "Session",
    delivery_id: int,
    po_number: str | None,
) -> None:
    from app.models import DeliveryDetail, DeliveryHeader

    hdr = db.get(DeliveryHeader, delivery_id)
    if not hdr:
        raise HTTPException(status_code=404, detail="Delivery tidak ditemukan")
    if hdr.packing_id is None:
        raise HTTPException(
            status_code=400,
            detail="Delivery tanpa packing_id — tidak boleh ditagih",
        )
    if (hdr.status or "").lower() != "sent":
        raise HTTPException(
            status_code=400,
            detail="Invoice hanya boleh setelah delivery status 'sent' (barang sudah dikirim)",
        )
    details = db.scalars(
        select(DeliveryDetail).where(DeliveryDetail.delivery_id == delivery_id)
    ).all()
    if not details:
        raise HTTPException(
            status_code=400,
            detail="Delivery harus punya minimal satu baris detail sebelum invoice",
        )
    if po_number:
        pns = po_numbers_from_delivery(db, delivery_id)
        if pns and po_number.strip() not in pns:
            raise HTTPException(
                status_code=400,
                detail=f"po_number {po_number!r} tidak cocok dengan SO pada delivery ini: {sorted(pns)}",
            )
