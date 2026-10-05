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
def _po_details_from_delivery(db: "Session", delivery_id: int) -> list:
    from app.models import DeliveryDetail, PoDetail, ProductionDetail

    details = db.scalars(
        select(DeliveryDetail).where(DeliveryDetail.delivery_id == delivery_id)
    ).all()
    found = []
    seen_ids: set[int] = set()
    for d in details:
        pod = None
        if d.po_detail_id:
            pod = db.get(PoDetail, d.po_detail_id)
        elif d.production_detail_id:
            pd = db.get(ProductionDetail, d.production_detail_id)
            if pd and pd.po_detail_id:
                pod = db.get(PoDetail, pd.po_detail_id)
        if not pod or pod.po_id is None:
            continue
        if int(pod.id) in seen_ids:
            continue
        seen_ids.add(int(pod.id))
        found.append(pod)
    return found


def po_ids_from_delivery(db: "Session", delivery_id: int) -> set[int]:
    return {int(pod.po_id) for pod in _po_details_from_delivery(db, delivery_id) if pod.po_id}


def po_id_from_delivery(db: "Session", delivery_id: int) -> int | None:
    """Satu SO untuk header invoice. Delivery MRP memakai po_detail_id, bukan packing.production_id."""
    from app.models import DeliveryHeader, PackingHeader, ProductionOrder

    ids = po_ids_from_delivery(db, delivery_id)
    hdr = db.get(DeliveryHeader, delivery_id)
    if hdr and hdr.packing_id:
        packing = db.get(PackingHeader, hdr.packing_id)
        if packing and packing.production_id:
            production = db.get(ProductionOrder, packing.production_id)
            if production and production.po_id:
                ids.add(int(production.po_id))
    if len(ids) == 1:
        return next(iter(ids))
    return None


def po_numbers_from_delivery(db: "Session", delivery_id: int) -> set[str]:
    from app.models import PoHeader

    seen: set[str] = set()
    for pod in _po_details_from_delivery(db, delivery_id):
        ph = db.get(PoHeader, pod.po_id)
        if ph and ph.po_number:
            seen.add(ph.po_number)
    return seen


def joined_po_numbers_for_delivery(db: "Session", delivery_id: int, *, max_len: int = 100) -> str:
    """Nomor SO gabungan untuk header invoice multi-SO (kolom po_number max 100)."""
    pns = sorted(po_numbers_from_delivery(db, delivery_id))
    if not pns:
        return ""
    return " / ".join(pns)[:max_len]


def _packing_ids_for_delivery(
    db: "Session",
    hdr,
    details: list | None = None,
) -> set[int]:
    from app.models import DeliveryDetail, PackingDetail

    pids: set[int] = set()
    if hdr and getattr(hdr, "packing_id", None):
        pids.add(int(hdr.packing_id))
    rows = details
    if rows is None:
        rows = list(
            db.scalars(select(DeliveryDetail).where(DeliveryDetail.delivery_id == hdr.id)).all()
        )
    for d in rows:
        pkd_id = getattr(d, "packing_detail_id", None)
        if not pkd_id:
            continue
        pkd = db.get(PackingDetail, int(pkd_id))
        if pkd and pkd.packing_id:
            pids.add(int(pkd.packing_id))
    return pids


def delivery_has_invpl_printed(db: "Session", delivery_id: int, details: list | None = None) -> bool:
    from app.models import DeliveryHeader, PackingHeader

    hdr = db.get(DeliveryHeader, delivery_id)
    if not hdr:
        return False
    for pid in _packing_ids_for_delivery(db, hdr, details):
        ph = db.get(PackingHeader, pid)
        if ph and ph.invpl_printed_at is not None:
            return True
    return False


def validate_invoice_against_delivery(
    db: "Session",
    delivery_id: int,
    po_number: str | None,
    *,
    allow_draft: bool = False,
    skip_if_exists: bool = True,
) -> None:
    from app.models import DeliveryDetail, DeliveryHeader, Invoice

    hdr = db.get(DeliveryHeader, delivery_id)
    if not hdr:
        raise HTTPException(status_code=404, detail="Delivery tidak ditemukan")
    existing = db.scalars(
        select(Invoice.id).where(Invoice.delivery_id == int(delivery_id)).limit(1)
    ).first()
    if existing and skip_if_exists:
        raise HTTPException(
            status_code=400,
            detail="Invoice untuk delivery ini sudah ada",
        )
    status = (hdr.status or "").lower()
    if not allow_draft and status != "sent":
        raise HTTPException(
            status_code=400,
            detail="Invoice hanya boleh setelah delivery status 'sent' (barang sudah dikirim)",
        )
    if allow_draft and status not in ("draft", "sent"):
        raise HTTPException(
            status_code=400,
            detail=f"Delivery status {status!r} tidak boleh di-invoice",
        )
    details = db.scalars(
        select(DeliveryDetail).where(DeliveryDetail.delivery_id == delivery_id)
    ).all()
    if not details:
        raise HTTPException(
            status_code=400,
            detail="Delivery harus punya minimal satu baris detail sebelum invoice",
        )
    if hdr.packing_id is None and not allow_draft:
        related = _packing_ids_for_delivery(db, hdr, details)
        if related and not delivery_has_invpl_printed(db, delivery_id, details):
            raise HTTPException(
                status_code=400,
                detail="Delivery tanpa packing_id — cetak INVPL dulu sebelum invoice",
            )
    if po_number:
        pns = po_numbers_from_delivery(db, delivery_id)
        raw = po_number.strip()
        if pns and raw not in pns:
            joined = joined_po_numbers_for_delivery(db, delivery_id)
            parts = {p.strip() for p in raw.replace(",", "/").split("/") if p.strip()}
            if raw != joined and (not parts or not parts.issubset(pns)):
                raise HTTPException(
                    status_code=400,
                    detail=f"po_number {po_number!r} tidak cocok dengan SO pada delivery ini: {sorted(pns)}",
                )
