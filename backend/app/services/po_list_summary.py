"""Ringkasan baris detail untuk daftar header PO (material hint, ETD, jumlah baris)."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, TypedDict

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.models import PoDetail, PoHeader
from app.services.mkt_workflow import get_stuck_reason
from app.services.po_header_snapshots import resolve_header_snapshots_for_list

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class PoListSummary(TypedDict):
    detail_line_count: int
    material_hint: str | None
    etd_display: str | None


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

    unique = sorted(set(dates))
    if not unique:
        return None

    first = unique[0].isoformat()
    line_count = len(detail_rows)
    if len(unique) > 1:
        return f"{first} +{len(unique) - 1}"
    if line_count > 1:
        return f"{first} +{line_count - 1}"
    return first


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
            "etd_display": build_etd_display(header_etd_map.get(po_id), po_details),
        }
    return out


def attach_po_list_summaries(db: Session, items: list[PoHeader]) -> None:
    """Isi material_hint, etd_display & detail_line_count pada instance PoHeader (in-place)."""
    if not items:
        return
    summaries = compute_po_list_summaries(db, [p.id for p in items])
    for po in items:
        summary = summaries.get(
            po.id,
            {"detail_line_count": 0, "material_hint": None, "etd_display": None},
        )
        po.detail_line_count = summary["detail_line_count"]
        po.material_hint = summary["material_hint"]
        po.etd_display = summary["etd_display"]


def serialize_po_headers_for_list(db: Session, items: list[PoHeader]) -> list:
    """Enrich header PO untuk response API (snapshot, material, ETD, stuck reason)."""
    from app.schemas import PoHeaderOut

    for po in items:
        po.stuck_reason = get_stuck_reason(db, po.id)
    resolve_header_snapshots_for_list(db, items)
    attach_po_list_summaries(db, items)
    return [PoHeaderOut.model_validate(po) for po in items]
