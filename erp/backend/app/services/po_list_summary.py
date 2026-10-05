"""Ringkasan baris detail untuk daftar header PO (material hint, ETD, jumlah baris)."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, TypedDict

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.models import PoDetail, PoHeader
from app.services.mkt_workflow import attach_stuck_reasons_batch
from app.services.po_header_snapshots import resolve_header_snapshots_for_list

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class PoListSummary(TypedDict):
    detail_line_count: int
    material_hint: str | None
    lot_hint: str | None
    etd_display: str | None
    reply_etd_display: str | None


def build_material_hint(first_material: str | None, line_count: int) -> str | None:
    """Material pertama + suffix +N jika PO punya lebih dari satu baris detail."""
    if line_count <= 0:
        return None
    mat = (first_material or "").strip()
    if not mat:
        return None
    if line_count <= 1:
        return mat
    return f"{mat} +{line_count - 1}"


def build_lot_hint(detail_rows: list[PoDetail]) -> str | None:
    """No lot / THI lot: utamakan thi_line_ref, fallback system_reference (unik, dipisah koma)."""
    if not detail_rows:
        return None
    lots: list[str] = []
    seen: set[str] = set()
    for detail in detail_rows:
        lot = ""
        for val in (detail.thi_line_ref, detail.system_reference):
            if val and str(val).strip():
                lot = str(val).strip()
                break
        if not lot or lot in seen:
            continue
        seen.add(lot)
        lots.append(lot)
    if not lots:
        return None
    return ", ".join(lots)


def _format_date_summary(dates: list[date], line_count: int) -> str | None:
    unique = sorted(set(dates))
    if not unique:
        return None
    first = unique[0].isoformat()
    if len(unique) > 1:
        return f"{first} +{len(unique) - 1}"
    if line_count > 1:
        return f"{first} +{line_count - 1}"
    return first


def build_etd_display(header_etd: date | None, detail_rows: list[PoDetail]) -> str | None:
    """ETD header, fallback line_etd / jadwal kirim baris pertama (+N jika multi)."""
    if header_etd:
        return header_etd.isoformat()
    if not detail_rows:
        return None

    dates: list[date] = []
    for detail in detail_rows:
        if detail.line_etd:
            dates.append(detail.line_etd)
        for schedule in detail.delivery_schedules or []:
            if schedule.delivery_date:
                dates.append(schedule.delivery_date)

    return _format_date_summary(dates, len(detail_rows))


def build_reply_etd_display(detail_rows: list[PoDetail]) -> str | None:
    """Reply ETD dari line_etd baris detail — tampilkan tanggal unik langsung (bukan +N)."""
    if not detail_rows:
        return None
    unique = sorted({detail.line_etd for detail in detail_rows if detail.line_etd})
    if not unique:
        return None
    return ", ".join(d.isoformat() for d in unique)


def compute_po_list_summaries(db: Session, po_ids: list[int]) -> dict[int, PoListSummary]:
    """Hitung ringkasan list per PO id."""
    if not po_ids:
        return {}

    headers = list(db.scalars(select(PoHeader).where(PoHeader.id.in_(po_ids))).all())
    header_etd_map = {h.id: h.etd for h in headers}

    counts_rows = db.execute(
        select(PoDetail.po_id, func.count(PoDetail.id))
        .where(PoDetail.po_id.in_(po_ids))
        .group_by(PoDetail.po_id)
    ).all()
    counts = {po_id: int(cnt) for po_id, cnt in counts_rows}

    details = list(
        db.scalars(
            select(PoDetail)
            .options(selectinload(PoDetail.delivery_schedules))
            .where(PoDetail.po_id.in_(po_ids))
            .order_by(PoDetail.po_id, PoDetail.id)
        ).all()
    )

    details_by_po: dict[int, list[PoDetail]] = {po_id: [] for po_id in po_ids}
    first_material: dict[int, str | None] = {}
    for detail in details:
        po_id = detail.po_id
        details_by_po.setdefault(po_id, []).append(detail)
        if po_id in first_material and first_material[po_id]:
            continue
        name = (detail.material_name or "").strip()
        if name:
            first_material[po_id] = name
        elif po_id not in first_material:
            first_material[po_id] = None

    out: dict[int, PoListSummary] = {}
    for po_id in po_ids:
        po_details = details_by_po.get(po_id, [])
        cnt = counts.get(po_id, 0)
        out[po_id] = {
            "detail_line_count": cnt,
            "material_hint": build_material_hint(first_material.get(po_id), cnt),
            "lot_hint": build_lot_hint(po_details),
            "etd_display": build_etd_display(header_etd_map.get(po_id), po_details),
            "reply_etd_display": build_reply_etd_display(po_details),
        }
    return out


def attach_po_list_summaries(db: Session, items: list[PoHeader]) -> None:
    """Isi material_hint, lot_hint, etd_display, reply_etd_display & detail_line_count pada instance PoHeader."""
    if not items:
        return
    summaries = compute_po_list_summaries(db, [p.id for p in items])
    for po in items:
        summary = summaries.get(
            po.id,
            {
                "detail_line_count": 0,
                "material_hint": None,
                "lot_hint": None,
                "etd_display": None,
                "reply_etd_display": None,
            },
        )
        po.detail_line_count = summary["detail_line_count"]
        po.material_hint = summary["material_hint"]
        po.lot_hint = summary["lot_hint"]
        po.etd_display = summary["etd_display"]
        po.reply_etd_display = summary["reply_etd_display"]


def attach_mrp_sync_errors(db: Session, items: list[PoHeader]) -> None:
    """Badge mrp_sync_error dari notifikasi sync terakhir (tanpa kolom baru)."""
    from app.models import Notification

    ids = [int(p.id) for p in items if getattr(p, "id", None)]
    if not ids:
        return
    rows = (
        db.query(Notification.entity_id, Notification.message, Notification.id)
        .filter(
            Notification.category == "mrp",
            Notification.entity_type == "sales_order",
            Notification.title == "MRP sync gagal",
            Notification.entity_id.in_(ids),
        )
        .order_by(Notification.id.desc())
        .all()
    )
    latest: dict[int, str] = {}
    for eid, msg, _nid in rows:
        if eid is None:
            continue
        sid = int(eid)
        if sid in latest:
            continue
        latest[sid] = (msg or "").strip() or "MRP sync gagal"
    for po in items:
        err = latest.get(int(po.id))
        if err:
            po.mrp_sync_error = err


def serialize_po_headers_for_list(db: Session, items: list[PoHeader]) -> list:
    """Enrich header PO untuk response API (snapshot, material, ETD, stuck reason)."""
    from app.schemas import PoHeaderOut

    attach_stuck_reasons_batch(db, items)
    resolve_header_snapshots_for_list(db, items)
    attach_po_list_summaries(db, items)
    attach_mrp_sync_errors(db, items)
    return [PoHeaderOut.model_validate(po) for po in items]
