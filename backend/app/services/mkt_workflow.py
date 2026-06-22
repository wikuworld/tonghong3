"""Alur MKT sesuai flowchart: tahapan berurutan + syarat advance + auto-advance."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from fastapi import HTTPException
from sqlalchemy import select

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

MKT_STAGES_ORDER = (
    "input_system",
    "rekap_printed",
    "with_ppic",
    "back_to_mkt",
    "in_outstanding",
    "material_followup",
    "delivery_arranged",
    "sj_invpl",
    "invoice_billing",
)


def mkt_stage_index(stage: str | None) -> int:
    s = (stage or "input_system").strip() or "input_system"
    try:
        return MKT_STAGES_ORDER.index(s)
    except ValueError:
        return 0


def next_mkt_stage(current: str | None) -> str | None:
    i = mkt_stage_index(current)
    if i + 1 >= len(MKT_STAGES_ORDER):
        return None
    return MKT_STAGES_ORDER[i + 1]


def prev_mkt_stage(current: str | None) -> str | None:
    i = mkt_stage_index(current)
    if i <= 0:
        return None
    return MKT_STAGES_ORDER[i - 1]


def po_has_delivery_for_po(db: "Session", po_id: int) -> bool:
    from app.models import DeliveryDetail, DeliveryHeader, PoDetail, ProductionDetail

    row = db.scalars(
        select(DeliveryHeader.id)
        .join(DeliveryDetail, DeliveryDetail.delivery_id == DeliveryHeader.id)
        .join(ProductionDetail, ProductionDetail.id == DeliveryDetail.production_detail_id)
        .join(PoDetail, PoDetail.id == ProductionDetail.po_detail_id)
        .where(PoDetail.po_id == po_id)
        .limit(1)
    ).first()
    return row is not None


def po_has_sj_invpl_prints(db: "Session", po_id: int) -> bool:
    """Minimal satu delivery untuk PO ini: SJ + INVPL (packing terkait) sudah dicetak."""
    from app.models import Customer, DeliveryDetail, DeliveryHeader, PackingHeader, PoDetail, ProductionDetail

    rows = db.scalars(
        select(DeliveryHeader)
        .join(DeliveryDetail, DeliveryDetail.delivery_id == DeliveryHeader.id)
        .join(ProductionDetail, ProductionDetail.id == DeliveryDetail.production_detail_id)
        .join(PoDetail, PoDetail.id == ProductionDetail.po_detail_id)
        .where(PoDetail.po_id == po_id)
    ).all()
    if not rows:
        return False
    for dh in rows:
        if not dh.packing_id:
            continue
        pk = db.get(PackingHeader, dh.packing_id)
        if not pk or pk.invpl_printed_at is None:
            continue
        cust = db.get(Customer, dh.customer_id) if dh.customer_id else None
        export = bool(cust and getattr(cust, "is_export_customer", False))
        if export:
            return True
        if dh.surat_jalan_printed_at is not None:
            return True
    return False


def po_has_invoice_for_po(db: "Session", po_id: int) -> bool:
    from app.models import DeliveryDetail, DeliveryHeader, Invoice, PoDetail, ProductionDetail

    row = db.scalars(
        select(Invoice.id)
        .join(DeliveryHeader, DeliveryHeader.id == Invoice.delivery_id)
        .join(DeliveryDetail, DeliveryDetail.delivery_id == DeliveryHeader.id)
        .join(ProductionDetail, ProductionDetail.id == DeliveryDetail.production_detail_id)
        .join(PoDetail, PoDetail.id == ProductionDetail.po_detail_id)
        .where(PoDetail.po_id == po_id)
        .limit(1)
    ).first()
    return row is not None


def po_has_ppic_assignment(db: "Session", po_id: int) -> bool:
    from app.models import PpicsAssignment

    row = db.scalars(
        select(PpicsAssignment).where(PpicsAssignment.po_id == po_id).limit(1)
    ).first()
    return row is not None


def po_ppic_is_complete(db: "Session", po_id: int) -> bool:
    from app.models import PpicsAssignment

    row = db.scalars(
        select(PpicsAssignment)
        .where(PpicsAssignment.po_id == po_id, PpicsAssignment.status == "completed")
        .limit(1)
    ).first()
    return row is not None


def get_stuck_reason(db: "Session", po_id: int) -> str | None:
    """Return reason why PO is stuck, or None if ready to advance."""
    from app.models import PoHeader

    row = db.get(PoHeader, po_id)
    if not row:
        return None

    current_stage = (row.mkt_workflow_stage or "input_system").strip()
    nxt = next_mkt_stage(current_stage)

    if nxt is None:
        return None

    if nxt == "rekap_printed":
        if not row.rekap_printed_at:
            return "Menunggu rekap PO diprint"
        if row.status != "confirmed":
            return "PO belum di-confirm"

    elif nxt == "with_ppic":
        if not po_has_ppic_assignment(db, po_id):
            return "Belum di-assign ke PPIC"

    elif nxt == "back_to_mkt":
        if not po_ppic_is_complete(db, po_id):
            return "Menunggu PPIC menyelesaikan tugas"

    elif nxt == "in_outstanding":
        if not po_ppic_is_complete(db, po_id):
            return "Menunggu PPIC menyelesaikan tugas"

    elif nxt == "material_followup":
        if not row.material_followup_done:
            return "Material belum di-follow up"

    elif nxt == "delivery_arranged":
        if not row.material_followup_done:
            return "Material belum selesai di-follow up"
        if not po_has_delivery_for_po(db, po_id):
            return "Delivery belum dibuat"

    elif nxt == "sj_invpl":
        if not po_has_sj_invpl_prints(db, po_id):
            return "SJ/INVPL belum dicetak"

    elif nxt == "invoice_billing":
        if not po_has_invoice_for_po(db, po_id):
            return "Invoice belum dibuat"

    return None


def auto_advance_if_ready(db: "Session", po_id: int) -> str | None:
    """Auto-advance PO to next stage if conditions are met. Returns new stage or None."""
    from app.models import PoHeader

    row = db.get(PoHeader, po_id)
    if not row:
        return None

    current_stage = (row.mkt_workflow_stage or "input_system").strip()
    nxt = next_mkt_stage(current_stage)

    if nxt is None:
        return None

    stuck_reason = get_stuck_reason(db, po_id)
    if stuck_reason is not None:
        return None

    now = datetime.utcnow()
    row.mkt_workflow_stage = nxt
    row.mkt_workflow_updated_at = now

    if nxt == "rekap_printed" and row.rekap_printed_at is None:
        row.rekap_printed_at = now

    return nxt


def sync_mkt_workflow_auto_advance(
    db: "Session",
    po_id: int,
    *,
    actor: str = "system",
) -> list[str]:
    """Naikkan tahap MKT berurutan selama syarat terpenuhi (maks. satu putaran penuh)."""
    from app.services.audit import log_change

    advanced: list[str] = []
    for _ in range(len(MKT_STAGES_ORDER)):
        new_stage = auto_advance_if_ready(db, po_id)
        if not new_stage:
            break
        advanced.append(new_stage)
        log_change(
            db,
            entity_type="sales_order",
            entity_id=po_id,
            action="auto_advance",
            after={"mkt_workflow_stage": new_stage},
            actor=actor,
        )
    return advanced


def sync_mkt_for_delivery(
    db: "Session",
    delivery_id: int,
    *,
    actor: str = "system",
) -> None:
    """Auto-advance semua PO pada delivery."""
    from app.models import PoHeader

    from app.services.business_rules import po_numbers_from_delivery

    for pn in po_numbers_from_delivery(db, delivery_id):
        ph = db.scalars(select(PoHeader).where(PoHeader.po_number == pn).limit(1)).first()
        if ph:
            sync_mkt_workflow_auto_advance(db, ph.id, actor=actor)


def sync_mkt_for_packing(
    db: "Session",
    packing_id: int,
    *,
    actor: str = "system",
) -> None:
    """Auto-advance PO terkait packing (via delivery yang memakai packing ini)."""
    from app.models import DeliveryHeader

    rows = db.scalars(
        select(DeliveryHeader).where(DeliveryHeader.packing_id == packing_id)
    ).all()
    for dh in rows:
        sync_mkt_for_delivery(db, dh.id, actor=actor)


def validate_mkt_advance(
    db: "Session",
    po_id: int,
    target: str,
) -> None:
    from app.models import PoHeader

    row = db.get(PoHeader, po_id)
    if not row:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")

    cur = (row.mkt_workflow_stage or "input_system").strip()
    nxt = next_mkt_stage(cur)
    if nxt is None:
        raise HTTPException(status_code=400, detail="PO sudah di tahap akhir alur MKT")
    if target != nxt:
        raise HTTPException(
            status_code=400,
            detail=f"Langkah MKT berikutnya harus {nxt!r}, bukan {target!r}",
        )

    stuck = get_stuck_reason(db, po_id)
    if stuck:
        raise HTTPException(status_code=400, detail=stuck)


def apply_mkt_stage(
    db: "Session",
    po_id: int,
    target: str,
) -> None:
    from app.models import PoHeader

    row = db.get(PoHeader, po_id)
    if not row:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")
    now = datetime.utcnow()
    row.mkt_workflow_stage = target
    row.mkt_workflow_updated_at = now
    if target == "rekap_printed" and row.rekap_printed_at is None:
        row.rekap_printed_at = now


def stamp_rekap_printed_for_recap(
    db: "Session",
    headers: list,
    *,
    actor: str | None = None,
) -> int:
    """Tandai rekap PO sudah dicetak/diunduh untuk header yang belum punya timestamp."""
    from app.models import PoHeader

    now = datetime.utcnow()
    stamped = 0
    for row in headers:
        if not isinstance(row, PoHeader):
            continue
        if row.rekap_printed_at is not None:
            continue
        row.rekap_printed_at = now
        stamped += 1
        if actor:
            from app.services.audit import log_change

            log_change(
                db,
                entity_type="sales_order",
                entity_id=row.id,
                action="rekap_printed",
                after={"rekap_printed_at": now.isoformat(), "po_number": row.po_number},
                actor=actor,
            )
    if stamped:
        db.commit()
    return stamped


def sync_invoice_billing_from_delivery(db: "Session", delivery_id: int) -> None:
    """Setelah invoice dibuat: naikkan tahap MKT ke invoice_billing untuk semua PO pada delivery."""
    from app.models import PoHeader

    from app.services.business_rules import po_numbers_from_delivery

    pns = po_numbers_from_delivery(db, delivery_id)
    now = datetime.utcnow()
    for pn in pns:
        ph = db.scalars(select(PoHeader).where(PoHeader.po_number == pn).limit(1)).first()
        if ph and mkt_stage_index(ph.mkt_workflow_stage) < mkt_stage_index("invoice_billing"):
            ph.mkt_workflow_stage = "invoice_billing"
            ph.mkt_workflow_updated_at = now
