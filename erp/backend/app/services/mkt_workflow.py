"""Alur MKT sesuai flowchart: tahapan berurutan + syarat advance + auto-advance."""

from __future__ import annotations

from app.timeutil import app_now
from typing import TYPE_CHECKING

from fastapi import HTTPException
from sqlalchemy import func, or_, select

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

# Tahap efektif (back_to_mkt digabung ke in_outstanding — lihat normalize_mkt_stage).
MKT_STAGES_ORDER = (
    "input_system",
    "rekap_printed",
    "with_ppic",
    "in_outstanding",
    "material_followup",
    "delivery_arranged",
    "sj_invpl",
    "invoice_billing",
)

# Alias historis → tahap kanonik (data lama / audit).
MKT_STAGE_ALIASES = {
    "back_to_mkt": "in_outstanding",
}

# Tahap yang tidak boleh di-rollback manual (dokumen/pengiriman).
MKT_ROLLBACK_LOCKED_STAGES = frozenset(
    {
        "delivery_arranged",
        "sj_invpl",
        "invoice_billing",
    }
)


def normalize_mkt_stage(stage: str | None) -> str:
    s = (stage or "input_system").strip() or "input_system"
    return MKT_STAGE_ALIASES.get(s, s)


def mkt_stage_index(stage: str | None) -> int:
    s = normalize_mkt_stage(stage)
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


def _delivery_status_posted():
    """Delivery yang menggerakkan tahap MKT: bukan draft, kosong, atau dibatalkan."""
    from app.models import DeliveryHeader

    st = func.lower(func.trim(func.coalesce(DeliveryHeader.status, "")))
    return st.notin_(("", "draft", "cancelled", "canceled"))


def _delivery_not_cancelled():
    from app.models import DeliveryHeader

    st = func.lower(func.trim(func.coalesce(DeliveryHeader.status, "")))
    return st.notin_(("cancelled", "canceled"))


def _direct_po_detail_delivery_clause():
    """Baris FG OUT: taut DeliveryDetail.po_detail_id tanpa ProductionDetail."""
    from app.models import DeliveryDetail

    return or_(
        DeliveryDetail.production_detail_id.is_(None),
        DeliveryDetail.production_detail_id == 0,
    )


def _stmt_delivery_ids_via_production(po_id: int, *, posted_only: bool = False):
    from app.models import DeliveryDetail, DeliveryHeader, PoDetail, ProductionDetail

    stmt = (
        select(DeliveryHeader.id)
        .join(DeliveryDetail, DeliveryDetail.delivery_id == DeliveryHeader.id)
        .join(ProductionDetail, ProductionDetail.id == DeliveryDetail.production_detail_id)
        .join(PoDetail, PoDetail.id == ProductionDetail.po_detail_id)
        .where(PoDetail.po_id == po_id)
    )
    if posted_only:
        stmt = stmt.where(_delivery_status_posted())
    return stmt


def _stmt_delivery_ids_via_direct(po_id: int, *, posted_only: bool = False):
    from app.models import DeliveryDetail, DeliveryHeader, PoDetail

    stmt = (
        select(DeliveryHeader.id)
        .join(DeliveryDetail, DeliveryDetail.delivery_id == DeliveryHeader.id)
        .join(PoDetail, PoDetail.id == DeliveryDetail.po_detail_id)
        .where(PoDetail.po_id == po_id, _direct_po_detail_delivery_clause())
    )
    if posted_only:
        stmt = stmt.where(_delivery_status_posted())
    return stmt


def _stmt_delivery_ids_for_po(po_id: int, *, posted_only: bool = False):
    return _stmt_delivery_ids_via_production(po_id, posted_only=posted_only).union(
        _stmt_delivery_ids_via_direct(po_id, posted_only=posted_only)
    )


def po_has_delivery_for_po(db: "Session", po_id: int) -> bool:
    row = db.scalars(_stmt_delivery_ids_for_po(po_id, posted_only=True)).first()
    return row is not None


def po_has_posted_delivery(
    db: "Session",
    po_id: int,
    *,
    exclude_delivery_id: int | None = None,
) -> bool:
    ids = [
        int(x)
        for x in db.scalars(_stmt_delivery_ids_for_po(po_id, posted_only=True)).all()
        if x is not None
    ]
    if exclude_delivery_id is not None:
        ids = [i for i in ids if i != int(exclude_delivery_id)]
    return bool(ids)


def reconcile_po_stage_after_delivery_cancel(
    db: "Session",
    po,
    *,
    actor: str = "system",
    exclude_delivery_id: int | None = None,
) -> bool:
    """Turunkan tahap hanya sampai material_followup bila tidak ada SJ terkirim lain."""
    from app.services.audit import log_change

    if po is None or getattr(po, "id", None) is None:
        return False
    if po_has_posted_delivery(db, int(po.id), exclude_delivery_id=exclude_delivery_id):
        return False
    current = normalize_mkt_stage(getattr(po, "mkt_workflow_stage", None))
    floor = "material_followup"
    if mkt_stage_index(current) <= mkt_stage_index(floor):
        return False
    before = po.mkt_workflow_stage
    po.mkt_workflow_stage = floor
    log_change(
        db,
        entity_type="sales_order",
        entity_id=int(po.id),
        action="reconcile_after_delivery_cancel",
        before={"mkt_workflow_stage": before},
        after={"mkt_workflow_stage": floor},
        actor=actor,
    )
    return True


def po_has_schedule_for_po(db: "Session", po_id: int) -> bool:
    return po_id in _po_ids_with_schedule(db, [po_id])


def po_has_sj_invpl_prints(db: "Session", po_id: int) -> bool:
    """Minimal satu delivery untuk PO ini: SJ + INVPL (packing terkait) sudah dicetak."""
    from app.models import Customer, DeliveryHeader, PackingHeader

    header_ids = [int(x) for x in db.scalars(_stmt_delivery_ids_for_po(po_id)).all() if x]
    if not header_ids:
        return False
    rows = list(db.scalars(select(DeliveryHeader).where(DeliveryHeader.id.in_(header_ids))).all())
    if not rows:
        return False
    for dh in rows:
        if (dh.status or "").strip().lower() in ("cancelled", "canceled"):
            continue
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
    from app.models import Invoice

    row = db.scalars(
        select(Invoice.id)
        .where(
            Invoice.delivery_id.in_(_stmt_delivery_ids_for_po(po_id)),
            Invoice.voided_at.is_(None),
        )
        .limit(1)
    ).first()
    return row is not None


AUTO_PPIC_PREFIX = "[auto]"

CONFIRMED_STATUSES = frozenset({"confirmed", "production", "completed"})
PRE_OUTSTANDING_STAGES = frozenset({"input_system", "rekap_printed", "with_ppic"})


def _status_is_confirmed(status: str | None) -> bool:
    return (status or "").strip().lower() in CONFIRMED_STATUSES


def _first_active_ppic_user(db: "Session"):
    """User aktif dengan role atau department PPIC (pool, bukan pilih per orang)."""
    from app.models import User

    return db.scalars(
        select(User)
        .where(
            User.is_active.is_(True),
            or_(
                func.lower(func.coalesce(User.role, "")) == "ppic",
                func.lower(func.coalesce(User.department, "")) == "ppic",
            ),
        )
        .order_by(User.id.asc())
    ).first()


def ensure_rekap_stamped_if_confirmed(db: "Session", po) -> bool:
    """Stempel arsip rekap saat SO sudah confirm — bukan gerbang tahap.

    Return True jika stempel baru ditulis.
    """
    if po is None or po.rekap_printed_at is not None:
        return False
    if not _status_is_confirmed(po.status):
        return False
    po.rekap_printed_at = app_now()
    return True


def _notify_ppic_entered_outstanding(db: "Session", po, *, actor: str) -> None:
    try:
        from app.services.notifications import create_notification_for_ppic_users

        pn = (po.po_number or "").strip() or str(po.id)
        q = {"po_id": po.id}
        if po.po_number:
            q["q"] = po.po_number
        create_notification_for_ppic_users(
            db,
            title=f"SO {pn} masuk Outstanding",
            message=f"SO dikonfirmasi dan siap dikerjakan PPIC ({actor}).",
            category="outstanding",
            entity_type="sales_order",
            entity_id=int(po.id) if po.id else None,
            route_path="/admin/marketing-flow/outstanding",
            route_query=q,
        )
    except Exception:
        pass


def po_has_ppic_assignment(db: "Session", po_id: int) -> bool:
    from app.models import PpicsAssignment

    row = db.scalars(
        select(PpicsAssignment)
        .where(
            PpicsAssignment.po_id == po_id,
            PpicsAssignment.status.in_(("pending", "in_progress", "completed")),
        )
        .limit(1)
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


def ensure_auto_ppic_handoff(db: "Session", po_id: int) -> bool:
    """Serah terima PPIC otomatis (pool) + tandai selesai — tanpa tombol di Daftar SO.

    Gerbang Outstanding = SO sudah confirm. Assignment pool opsional (audit);
    tidak ada user PPIC aktif tidak menahan tahap.
    """
    from app.models import PoHeader, PpicsAssignment

    po = db.get(PoHeader, po_id)
    if not po:
        return False
    if not _status_is_confirmed(po.status):
        return False

    active = db.scalars(
        select(PpicsAssignment)
        .where(
            PpicsAssignment.po_id == po_id,
            PpicsAssignment.status.in_(("pending", "in_progress", "completed")),
        )
        .order_by(PpicsAssignment.id.desc())
        .limit(1)
    ).first()
    now = app_now()
    if active:
        if active.status == "completed":
            return True
        active.status = "completed"
        active.completed_at = now
        note = (active.notes or "").strip()
        tag = f"{AUTO_PPIC_PREFIX} Selesai otomatis"
        if tag not in note:
            active.notes = f"{note}; {tag}".strip("; ") if note else tag
        db.flush()
        return True

    ppic_user = _first_active_ppic_user(db)
    if not ppic_user:
        return True

    db.add(
        PpicsAssignment(
            po_id=po_id,
            ppic_user_id=int(ppic_user.id),
            notes=f"{AUTO_PPIC_PREFIX} Serah terima & selesai otomatis ke tim PPIC",
            status="completed",
            assigned_at=now,
            completed_at=now,
        )
    )
    db.flush()
    return True


def invalidate_ppic_assignments_for_rollback(db: "Session", po_id: int, target_stage: str) -> None:
    """Saat rollback mundur melewati pintu PPIC, void assignment lama agar tidak auto-loncat ke outstanding."""
    from app.models import PpicsAssignment

    target = normalize_mkt_stage(target_stage)
    target_idx = mkt_stage_index(target)
    with_ppic_idx = mkt_stage_index("with_ppic")
    rows = list(
        db.scalars(select(PpicsAssignment).where(PpicsAssignment.po_id == po_id)).all()
    )
    if not rows:
        return

    if target_idx < with_ppic_idx:
        # Kembali sebelum «with_ppic»: wajib assign ulang.
        for a in rows:
            a.status = "cancelled"
            a.completed_at = None
            note = (a.notes or "").strip()
            tag = "[rollback: void assignment]"
            if tag not in note:
                a.notes = f"{note} {tag}".strip() if note else tag
    elif target == "with_ppic":
        # Kembali ke «with_ppic»: PPIC harus complete ulang.
        for a in rows:
            if a.status == "cancelled":
                continue
            a.status = "pending"
            a.completed_at = None
            note = (a.notes or "").strip()
            tag = "[rollback: reopen PPIC]"
            if tag not in note:
                a.notes = f"{note} {tag}".strip() if note else tag


def clear_rekap_printed_on_rollback(db: "Session", po_id: int, target_stage: str) -> None:
    """Rollback ke input_system → hapus stamp print agar cetak harus dikonfirmasi lagi."""
    from app.models import PoHeader

    if normalize_mkt_stage(target_stage) != "input_system":
        return
    row = db.get(PoHeader, po_id)
    if row and row.rekap_printed_at is not None:
        row.rekap_printed_at = None


def apply_mkt_rollback_side_effects(db: "Session", po_id: int, target_stage: str) -> None:
    clear_rekap_printed_on_rollback(db, po_id, target_stage)
    invalidate_ppic_assignments_for_rollback(db, po_id, target_stage)


def _stuck_reason_for_header(
  row,
  *,
  has_ppic: bool,
  ppic_complete: bool,
  has_delivery: bool,
  has_sj_invpl: bool,
  has_invoice: bool,
) -> str | None:
    """Hitung stuck reason dari header + flags yang sudah di-preload."""
    current_stage = normalize_mkt_stage(row.mkt_workflow_stage)
    nxt = next_mkt_stage(current_stage)

    if nxt is None:
        return None

    if nxt == "rekap_printed":
        if not _status_is_confirmed(row.status):
            return "PO belum di-confirm"

    elif nxt == "delivery_arranged":
        if not has_delivery:
            return "Delivery belum dibuat"

    elif nxt == "sj_invpl":
        if not has_sj_invpl:
            return "SJ/INVPL belum dicetak"

    elif nxt == "invoice_billing":
        if not has_invoice:
            return "Invoice belum dibuat"

    return None


def _po_ids_with_delivery(db: "Session", po_ids: list[int]) -> set[int]:
    from app.models import DeliveryDetail, DeliveryHeader, PoDetail, ProductionDetail

    if not po_ids:
        return set()
    via_prod = (
        select(PoDetail.po_id)
        .join(ProductionDetail, ProductionDetail.po_detail_id == PoDetail.id)
        .join(DeliveryDetail, DeliveryDetail.production_detail_id == ProductionDetail.id)
        .join(DeliveryHeader, DeliveryHeader.id == DeliveryDetail.delivery_id)
        .where(PoDetail.po_id.in_(po_ids), _delivery_status_posted())
    )
    via_direct = (
        select(PoDetail.po_id)
        .join(DeliveryDetail, DeliveryDetail.po_detail_id == PoDetail.id)
        .join(DeliveryHeader, DeliveryHeader.id == DeliveryDetail.delivery_id)
        .where(
            PoDetail.po_id.in_(po_ids),
            _direct_po_detail_delivery_clause(),
            _delivery_status_posted(),
        )
    )
    rows = db.scalars(via_prod.union(via_direct)).all()
    return {int(x) for x in rows if x is not None}


def _po_ids_with_schedule(db: "Session", po_ids: list[int]) -> set[int]:
    from app.models import PoDetail, PoDetailDelivery

    if not po_ids:
        return set()
    rows = db.scalars(
        select(PoDetail.po_id)
        .join(PoDetailDelivery, PoDetailDelivery.po_detail_id == PoDetail.id)
        .where(
            PoDetail.po_id.in_(po_ids),
            PoDetailDelivery.qty.is_not(None),
            PoDetailDelivery.qty > 0,
        )
        .distinct()
    ).all()
    return {int(x) for x in rows if x is not None}


def _po_ids_with_invoice(db: "Session", po_ids: list[int]) -> set[int]:
    from app.models import DeliveryDetail, DeliveryHeader, Invoice, PoDetail, ProductionDetail

    if not po_ids:
        return set()
    via_prod = (
        select(PoDetail.po_id)
        .join(ProductionDetail, ProductionDetail.po_detail_id == PoDetail.id)
        .join(DeliveryDetail, DeliveryDetail.production_detail_id == ProductionDetail.id)
        .join(DeliveryHeader, DeliveryHeader.id == DeliveryDetail.delivery_id)
        .join(Invoice, Invoice.delivery_id == DeliveryHeader.id)
        .where(
            PoDetail.po_id.in_(po_ids),
            _delivery_not_cancelled(),
            Invoice.voided_at.is_(None),
        )
    )
    via_direct = (
        select(PoDetail.po_id)
        .join(DeliveryDetail, DeliveryDetail.po_detail_id == PoDetail.id)
        .join(DeliveryHeader, DeliveryHeader.id == DeliveryDetail.delivery_id)
        .join(Invoice, Invoice.delivery_id == DeliveryHeader.id)
        .where(
            PoDetail.po_id.in_(po_ids),
            _direct_po_detail_delivery_clause(),
            _delivery_not_cancelled(),
            Invoice.voided_at.is_(None),
        )
    )
    rows = db.scalars(via_prod.union(via_direct)).all()
    return {int(x) for x in rows if x is not None}


def _build_stuck_reason_context(db: "Session", po_ids: list[int]) -> dict[int, dict[str, bool]]:
    if not po_ids:
        return {}

    has_ppic: set[int] = set()
    ppic_complete: set[int] = set()
    for po_id in po_ids:
        if po_has_ppic_assignment(db, po_id):
            has_ppic.add(po_id)
        if po_ppic_is_complete(db, po_id):
            ppic_complete.add(po_id)

    has_delivery = _po_ids_with_delivery(db, po_ids)
    has_invoice = _po_ids_with_invoice(db, po_ids)
    has_sj_invpl: set[int] = set()
    for po_id in po_ids:
        if po_has_sj_invpl_prints(db, po_id):
            has_sj_invpl.add(po_id)

    return {
        po_id: {
            "has_ppic": po_id in has_ppic,
            "ppic_complete": po_id in ppic_complete,
            "has_delivery": po_id in has_delivery,
            "has_sj_invpl": po_id in has_sj_invpl,
            "has_invoice": po_id in has_invoice,
        }
        for po_id in po_ids
    }


def attach_stuck_reasons_batch(db: "Session", headers: list) -> None:
    """Isi atribut stuck_reason pada instance PoHeader (in-place), batch-friendly."""
    if not headers:
        return
    po_ids = [int(h.id) for h in headers if getattr(h, "id", None) is not None]
    ctx = _build_stuck_reason_context(db, po_ids)
    for row in headers:
        if row.id is None:
            row.stuck_reason = None
            continue
        flags = ctx.get(int(row.id), {})
        row.stuck_reason = _stuck_reason_for_header(
            row,
            has_ppic=flags.get("has_ppic", False),
            ppic_complete=flags.get("ppic_complete", False),
            has_delivery=flags.get("has_delivery", False),
            has_sj_invpl=flags.get("has_sj_invpl", False),
            has_invoice=flags.get("has_invoice", False),
        )


def get_stuck_reason(db: "Session", po_id: int) -> str | None:
    """Return reason why PO is stuck, or None if ready to advance."""
    from app.models import PoHeader

    row = db.get(PoHeader, po_id)
    if not row:
        return None
    attach_stuck_reasons_batch(db, [row])
    return row.stuck_reason


def auto_advance_if_ready(db: "Session", po_id: int) -> str | None:
    """Auto-advance PO to next stage if conditions are met. Returns new stage or None."""
    from app.models import PoHeader

    row = db.get(PoHeader, po_id)
    if not row:
        return None

    current_stage = normalize_mkt_stage(row.mkt_workflow_stage)
    nxt = next_mkt_stage(current_stage)

    if nxt is None:
        return None

    if nxt == "rekap_printed":
        ensure_rekap_stamped_if_confirmed(db, row)

    # Assignment pool opsional — tidak menahan Confirm → Outstanding.
    if nxt in ("with_ppic", "in_outstanding"):
        ensure_auto_ppic_handoff(db, po_id)

    stuck_reason = get_stuck_reason(db, po_id)
    if stuck_reason is not None:
        return None

    # Gerbang jadwal hanya untuk auto-advance — lanjut manual tetap boleh tanpa slot.
    if nxt == "material_followup" and not po_has_schedule_for_po(db, po_id):
        return None

    now = app_now()
    row.mkt_workflow_stage = nxt
    row.mkt_workflow_updated_at = now
    if mkt_stage_index(nxt) >= mkt_stage_index("delivery_arranged"):
        row.material_followup_done = True

    return nxt


def sync_mkt_workflow_auto_advance(
    db: "Session",
    po_id: int,
    *,
    actor: str = "system",
    max_steps: int | None = None,
    stop_at_stage: str | None = None,
    notify_ppic: bool = True,
) -> list[str]:
    """Naikkan tahap MKT berurutan selama syarat terpenuhi.

    max_steps: batasi jumlah loncatan (None = satu putaran penuh pipeline).
    stop_at_stage: berhenti setelah mencapai tahap ini (tidak lanjut berikutnya).
    notify_ppic: kirim notifikasi ke semua user PPIC saat masuk Outstanding.
    """
    from app.models import PoHeader
    from app.services.audit import log_change

    limit = max_steps if max_steps is not None else len(MKT_STAGES_ORDER)
    stop = normalize_mkt_stage(stop_at_stage) if stop_at_stage else None
    advanced: list[str] = []
    for _ in range(max(0, limit)):
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
        if stop and normalize_mkt_stage(new_stage) == stop:
            break
    if notify_ppic and "in_outstanding" in advanced:
        po = db.get(PoHeader, po_id)
        if po:
            _notify_ppic_entered_outstanding(db, po, actor=actor)
    return advanced


def backfill_confirmed_to_outstanding(db: "Session", *, actor: str = "system") -> int:
    """Naikkan SO confirmed+ yang masih sebelum Outstanding (sekali, tanpa notifikasi)."""
    from app.models import PoHeader

    rows = list(
        db.scalars(
            select(PoHeader).where(
                func.lower(func.coalesce(PoHeader.status, "")).in_(tuple(CONFIRMED_STATUSES)),
                PoHeader.mkt_workflow_stage.in_(tuple(PRE_OUTSTANDING_STAGES)),
            )
        ).all()
    )
    moved = 0
    for row in rows:
        ensure_rekap_stamped_if_confirmed(db, row)
        sync_mkt_workflow_auto_advance(
            db,
            int(row.id),
            actor=actor,
            stop_at_stage="in_outstanding",
            notify_ppic=False,
        )
        if normalize_mkt_stage(row.mkt_workflow_stage) == "in_outstanding":
            moved += 1
    if moved:
        db.commit()
    return moved


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

    cur = normalize_mkt_stage(row.mkt_workflow_stage)
    nxt = next_mkt_stage(cur)
    target_norm = normalize_mkt_stage(target)
    if nxt is None:
        raise HTTPException(status_code=400, detail="PO sudah di tahap akhir alur MKT")
    if target_norm != nxt:
        raise HTTPException(
            status_code=400,
            detail=f"Langkah MKT berikutnya harus {nxt!r}, bukan {target!r}",
        )

    stuck = get_stuck_reason(db, po_id)
    if stuck:
        raise HTTPException(status_code=400, detail=stuck)


def validate_mkt_rollback(
    db: "Session",
    po_id: int,
    *,
    reason: str | None,
) -> tuple[str, str]:
    """Validasi rollback production-safe. Return (prev_stage, reason_clean)."""
    from app.models import PoHeader

    reason_clean = " ".join(str(reason or "").split()).strip()
    if len(reason_clean) < 5:
        raise HTTPException(
            status_code=400,
            detail="Alasan rollback wajib diisi (minimal 5 karakter)",
        )

    row = db.get(PoHeader, po_id)
    if not row:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")

    cur = normalize_mkt_stage(row.mkt_workflow_stage)
    prev = prev_mkt_stage(cur)
    if not prev:
        raise HTTPException(status_code=400, detail="PO sudah di tahap awal alur MKT")

    if cur in MKT_ROLLBACK_LOCKED_STAGES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Tidak bisa rollback dari tahap «{cur}»: "
                "tahap pengiriman/dokumen terkunci"
            ),
        )

    if po_has_invoice_for_po(db, po_id):
        raise HTTPException(
            status_code=400,
            detail="Tidak bisa rollback: invoice sudah dibuat untuk PO ini",
        )
    if po_has_delivery_for_po(db, po_id):
        raise HTTPException(
            status_code=400,
            detail="Tidak bisa rollback: delivery sudah dibuat untuk PO ini",
        )

    return prev, reason_clean


def apply_mkt_stage(
    db: "Session",
    po_id: int,
    target: str,
) -> None:
    from app.models import PoHeader

    row = db.get(PoHeader, po_id)
    if not row:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")
    now = app_now()
    row.mkt_workflow_stage = normalize_mkt_stage(target)
    row.mkt_workflow_updated_at = now
    if mkt_stage_index(row.mkt_workflow_stage) >= mkt_stage_index("delivery_arranged"):
        row.material_followup_done = True
    # Jangan auto-stamp rekap_printed_at di sini — hanya lewat dialog konfirmasi cetak.


def stamp_rekap_printed_for_recap(
    db: "Session",
    headers: list,
    *,
    actor: str | None = None,
) -> int:
    """Tandai rekap PO sudah dicetak (konfirmasi dari dialog HTML) untuk header tanpa timestamp."""
    from app.models import PoHeader

    now = app_now()
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
    now = app_now()
    for pn in pns:
        ph = db.scalars(select(PoHeader).where(PoHeader.po_number == pn).limit(1)).first()
        if ph and mkt_stage_index(ph.mkt_workflow_stage) < mkt_stage_index("invoice_billing"):
            ph.mkt_workflow_stage = "invoice_billing"
            ph.mkt_workflow_updated_at = now
