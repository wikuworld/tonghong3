"""Scan keluar gudang → tandai delivery sebagai sent (via no. SJ atau packing list)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from fastapi import HTTPException
from sqlalchemy import func, select

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def resolve_packing_id(
    db: "Session",
    *,
    packing_id: int | None = None,
    packing_number: str | None = None,
) -> int:
    from app.models import PackingHeader

    if packing_id:
        ph = db.get(PackingHeader, int(packing_id))
        if not ph:
            raise HTTPException(status_code=404, detail=f"Packing #{packing_id} tidak ditemukan")
        return int(ph.id)
    code = (packing_number or "").strip()
    if not code:
        raise HTTPException(
            status_code=400,
            detail="Isi packing_id atau packing_number (scan packing list)",
        )
    ph = db.scalars(
        select(PackingHeader).where(PackingHeader.packing_number == code).limit(1)
    ).first()
    if not ph:
        raise HTTPException(status_code=404, detail=f"Packing number {code!r} tidak ditemukan")
    return int(ph.id)


def resolve_delivery_by_number(db: "Session", delivery_number: str):
    """Cari DeliveryHeader by nomor SJ (exact, case-insensitive)."""
    from app.models import DeliveryHeader

    code = (delivery_number or "").strip()
    if not code:
        raise HTTPException(status_code=400, detail="Isi nomor surat jalan")
    hdr = db.scalars(
        select(DeliveryHeader)
        .where(func.lower(DeliveryHeader.delivery_number) == code.lower())
        .limit(1)
    ).first()
    if not hdr:
        raise HTTPException(status_code=404, detail=f"Surat jalan {code!r} tidak ditemukan")
    return hdr


def delivery_ids_for_packing(db: "Session", packing_id: int) -> list[int]:
    from app.models import DeliveryDetail, DeliveryHeader, PackingDetail

    ids: set[int] = set()
    for hid in db.scalars(
        select(DeliveryHeader.id).where(DeliveryHeader.packing_id == int(packing_id))
    ).all():
        ids.add(int(hid))

    pkd_ids = list(
        db.scalars(
            select(PackingDetail.id).where(PackingDetail.packing_id == int(packing_id))
        ).all()
    )
    if pkd_ids:
        for hid in db.scalars(
            select(DeliveryDetail.delivery_id)
            .where(DeliveryDetail.packing_detail_id.in_(pkd_ids))
            .distinct()
        ).all():
            if hid is not None:
                ids.add(int(hid))
    return sorted(ids)


def _mark_deliveries_sent(
    db: "Session",
    delivery_ids: list[int],
    *,
    actor: str,
    action: str,
    after_extra: dict[str, Any] | None = None,
    notify_title_fn=None,
    notify_message_fn=None,
) -> dict[str, Any]:
    from app.models import DeliveryDetail, DeliveryHeader
    from app.services.audit import log_change
    from app.services.mkt_workflow import sync_mkt_for_delivery
    from app.services.notifications import create_notification_for_roles

    marked: list[int] = []
    already_sent: list[int] = []
    skipped: list[dict[str, Any]] = []
    extra = after_extra or {}

    for did in delivery_ids:
        hdr = db.get(DeliveryHeader, did)
        if not hdr:
            continue
        status = (hdr.status or "").lower()
        if status == "sent":
            already_sent.append(did)
            continue
        if bool(getattr(hdr, "is_deleted", False)) or status in ("cancelled", "canceled"):
            skipped.append({"delivery_id": did, "reason": "deleted"})
            continue
        has_detail = db.scalars(
            select(DeliveryDetail.id).where(DeliveryDetail.delivery_id == did).limit(1)
        ).first()
        if not has_detail:
            skipped.append({"delivery_id": did, "reason": "no_details"})
            continue
        before = hdr.status
        hdr.status = "sent"
        log_change(
            db,
            entity_type="delivery",
            entity_id=hdr.id,
            action=action,
            before={"status": before},
            after={"status": "sent", **extra},
            actor=actor,
        )
        sync_mkt_for_delivery(db, hdr.id, actor=actor)
        try:
            title = (
                notify_title_fn(hdr)
                if notify_title_fn
                else f"Delivery {hdr.delivery_number or hdr.id} terkirim"
            )
            message = (
                notify_message_fn(hdr)
                if notify_message_fn
                else f"Status delivery #{hdr.id} → sent"
            )
            create_notification_for_roles(
                db,
                ("admin", "warehouse", "finance", "marketing"),
                title=title,
                message=message,
                category="delivery",
                entity_type="delivery",
                entity_id=hdr.id,
                route_path="/admin/delivery",
                route_query={"delivery_id": hdr.id},
            )
        except Exception:
            pass
        marked.append(did)

    db.commit()
    return {
        "marked_sent": marked,
        "already_sent": already_sent,
        "skipped": skipped,
    }


def scan_surat_jalan_out(
    db: "Session",
    *,
    delivery_number: str,
    actor: str = "system",
) -> dict[str, Any]:
    """Set status=sent untuk satu SJ by nomor (contoh THI-M260921002). Idempotent."""
    hdr = resolve_delivery_by_number(db, delivery_number)
    code = (hdr.delivery_number or "").strip()
    result = _mark_deliveries_sent(
        db,
        [int(hdr.id)],
        actor=actor,
        action="scan_out_surat_jalan",
        after_extra={"delivery_number": code},
        notify_title_fn=lambda h: f"Delivery {h.delivery_number or h.id} terkirim (scan SJ)",
        notify_message_fn=lambda h: f"Auto-sent dari scan surat jalan {h.delivery_number or h.id}",
    )
    marked = result["marked_sent"]
    already = result["already_sent"]
    return {
        "ok": True,
        "packing_id": None,
        "delivery_id": int(hdr.id),
        "delivery_number": code or None,
        "marked_sent": marked,
        "already_sent": already,
        "skipped": result["skipped"],
        "message": (
            f"SJ {code or hdr.id}: ditandai sent"
            if marked
            else (
                f"SJ {code or hdr.id}: sudah sent"
                if already
                else f"SJ {code or hdr.id}: tidak diubah"
            )
        ),
    }


def scan_packing_list_out(
    db: "Session",
    *,
    packing_id: int | None = None,
    packing_number: str | None = None,
    actor: str = "system",
) -> dict[str, Any]:
    """Set status=sent untuk semua delivery draft terkait packing. Idempotent."""
    pid = resolve_packing_id(db, packing_id=packing_id, packing_number=packing_number)
    delivery_ids = delivery_ids_for_packing(db, pid)
    if not delivery_ids:
        raise HTTPException(
            status_code=404,
            detail=f"Tidak ada surat jalan untuk packing #{pid}",
        )

    result = _mark_deliveries_sent(
        db,
        delivery_ids,
        actor=actor,
        action="scan_out_packing_list",
        after_extra={"packing_id": pid},
        notify_title_fn=lambda h: f"Delivery {h.delivery_number or h.id} terkirim (scan packing)",
        notify_message_fn=lambda _h: f"Auto-sent dari scan packing list #{pid}",
    )
    marked = result["marked_sent"]
    already_sent = result["already_sent"]
    return {
        "ok": True,
        "packing_id": pid,
        "delivery_id": marked[0] if len(marked) == 1 else (already_sent[0] if len(already_sent) == 1 else None),
        "delivery_number": None,
        "marked_sent": marked,
        "already_sent": already_sent,
        "skipped": result["skipped"],
        "message": (
            f"Packing #{pid}: {len(marked)} SJ ditandai sent"
            + (f", {len(already_sent)} sudah sent" if already_sent else "")
        ),
    }


def scan_out(
    db: "Session",
    *,
    delivery_number: str | None = None,
    packing_id: int | None = None,
    packing_number: str | None = None,
    actor: str = "system",
) -> dict[str, Any]:
    """Utama: scan no. SJ. Fallback: packing id/number (kompatibilitas E2E)."""
    sj = (delivery_number or "").strip()
    if sj:
        return scan_surat_jalan_out(db, delivery_number=sj, actor=actor)
    if packing_id or (packing_number or "").strip():
        return scan_packing_list_out(
            db,
            packing_id=packing_id,
            packing_number=packing_number,
            actor=actor,
        )
    raise HTTPException(
        status_code=400,
        detail="Isi nomor surat jalan (contoh THI-M260921002)",
    )
