"""Baca alokasi rencana MRP (tbl_master_po) via HTTP — bukan join DB MRP."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config import settings

log = logging.getLogger(__name__)

MRP_UNSYNCED = "unsynced"
_ALLOC_STATUSES = frozenset({"outstanding", "partial", "completed", "cancelled"})


def _upstream_url() -> str:
    return (settings.mrp_upstream_url or "http://mrp:5010").rstrip("/")


def _qty_str(v: float) -> str:
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return f"{v:.2f}".rstrip("0").rstrip(".")


def unsynced_mrp_alloc() -> dict[str, str]:
    return {
        "mrp_alloc_status": MRP_UNSYNCED,
        "mrp_qty_processed": "",
        "mrp_qty_remaining": "",
    }


def parse_mrp_alloc_row(item: dict[str, Any] | None) -> dict[str, str]:
    if not isinstance(item, dict):
        return unsynced_mrp_alloc()
    try:
        qty_order = float(item.get("qty_order") or 0)
    except (TypeError, ValueError):
        qty_order = 0.0
    try:
        qty_processed = float(item.get("qty_processed") or 0)
    except (TypeError, ValueError):
        qty_processed = 0.0
    remaining = max(0.0, qty_order - qty_processed)
    status = str(item.get("status") or "").strip().lower()
    if status not in _ALLOC_STATUSES:
        status = MRP_UNSYNCED
    return {
        "mrp_alloc_status": status,
        "mrp_qty_processed": _qty_str(qty_processed) if status != MRP_UNSYNCED else "",
        "mrp_qty_remaining": _qty_str(remaining) if status != MRP_UNSYNCED else "",
    }


def fetch_mrp_alloc_by_detail_ids(
    detail_ids: list[int],
    *,
    timeout: float = 4.0,
) -> dict[int, dict[str, str]]:
    """Map source_detail_id → alokasi. Gagal/timeout → dict kosong (caller isi unsynced)."""
    ids = sorted({int(x) for x in detail_ids if x is not None})
    if not ids:
        return {}
    csv = ",".join(str(i) for i in ids)
    target = f"{_upstream_url()}/api/mrp/masters/po?source_detail_ids={csv}"
    try:
        with httpx.Client(timeout=timeout) as client:
            upstream = client.get(target)
        if upstream.status_code >= 400:
            log.warning("mrp_po_alloc HTTP %s: %s", upstream.status_code, upstream.text[:200])
            return {}
        data = upstream.json() if upstream.content else []
    except Exception as exc:
        log.warning("mrp_po_alloc failed: %s", exc)
        return {}
    if not isinstance(data, list):
        return {}
    out: dict[int, dict[str, str]] = {}
    for item in data:
        if not isinstance(item, dict):
            continue
        sid = item.get("source_detail_id")
        try:
            sid_i = int(sid)
        except (TypeError, ValueError):
            continue
        out[sid_i] = parse_mrp_alloc_row(item)
    return out


def enrich_outstanding_mrp_alloc(rows: list[dict[str, Any]]) -> None:
    """Isi field alokasi MRP in-place. Baris tanpa match = unsynced."""
    ids = [int(r["po_detail_id"]) for r in rows if r.get("po_detail_id") is not None]
    found = fetch_mrp_alloc_by_detail_ids(ids)
    blank = unsynced_mrp_alloc()
    for row in rows:
        sid = row.get("po_detail_id")
        try:
            sid_i = int(sid)
        except (TypeError, ValueError):
            row.update(blank)
            continue
        row.update(found.get(sid_i) or blank)
