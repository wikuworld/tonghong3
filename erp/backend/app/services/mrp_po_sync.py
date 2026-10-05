"""Push / sync baris PO Tonghong → MRP tbl_master_po."""

from __future__ import annotations

import logging
import time
from decimal import Decimal
from typing import Any, Optional

import httpx
from sqlalchemy.orm import Session, selectinload

from app.config import settings
from app.models import PoDetail, PoHeader

log = logging.getLogger(__name__)

_CANCELLED_STATUSES = frozenset({"cancelled", "canceled", "void"})
_SYNCABLE_STATUSES = frozenset({"confirmed", "production", "completed"})
_PUSH_MAX_ATTEMPTS = 3
_PUSH_RETRY_BACKOFF_SEC = 0.5


def _num(v: Any) -> float:
    if v is None:
        return 0.0
    if isinstance(v, Decimal):
        return float(v)
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _thickness_text(d: PoDetail) -> str:
    if d.thickness_text:
        return str(d.thickness_text).strip()
    if d.thickness_min is not None and d.thickness_max is not None:
        return f"{d.thickness_min}-{d.thickness_max}"
    if d.thickness_min is not None:
        return str(d.thickness_min)
    return ""


def map_po_detail(d: PoDetail, *, force_cancelled: bool = False) -> Optional[dict]:
    po: Optional[PoHeader] = d.po
    if not po:
        return None
    no_so = (po.po_number or "").strip()
    no_po = (po.po_customer_ref or po.po_number or "").strip()
    if not no_po:
        return None
    item_name = (d.material_name or d.style_article or f"LINE-{d.id}").strip()
    # MRP rencana memakai color_swatch = factory_key (bukan color_code / color_reference).
    swatch = ""
    if d.color_swatch_recipe is not None:
        swatch = (getattr(d.color_swatch_recipe, "factory_key", None) or "").strip()
    qty_order = _num(d.quantity_order)
    qty_balance = _num(d.balance_qty) if d.balance_qty is not None else qty_order
    lot_number = (d.thi_line_ref or d.system_reference or "").strip() or None
    cancelled = force_cancelled or (po.status or "").strip().lower() in _CANCELLED_STATUSES
    payload = {
        "source_detail_id": d.id,
        "no_po": no_po,
        "no_so": no_so or None,
        "lot_number": lot_number,
        "customer": (po.customer_name_snapshot or po.customer_code or "").strip() or None,
        "customer_id": int(po.customer_id) if po.customer_id else None,
        "item_name": item_name,
        "warna": (d.color or "").strip(),
        "tebal": _thickness_text(d),
        "emboss": (d.emboss or "").strip(),
        "color_swatch": swatch or None,
        "sq_ft": qty_order,
        "qty_order": qty_order,
        "qty_balance_erp": qty_balance,
    }
    if cancelled:
        payload["cancelled"] = True
    return payload


def _upstream_url() -> str:
    return (settings.mrp_upstream_url or "http://127.0.0.1:8002").rstrip("/")


def _push_items(items: list[dict], *, timeout: float | None = None) -> dict:
    if not items:
        return {
            "ok": True,
            "inserted": 0,
            "updated": 0,
            "total": 0,
            "detail": "no PO lines",
            "attempts": 1,
        }
    if timeout is None:
        timeout = float(settings.mrp_sync_timeout_seconds or 12.0)
    target = f"{_upstream_url()}/api/mrp/masters/po/sync"
    last_exc: Exception | None = None
    for attempt in range(1, _PUSH_MAX_ATTEMPTS + 1):
        try:
            with httpx.Client(timeout=timeout) as client:
                upstream = client.post(target, json={"items": items})
            if upstream.status_code >= 400:
                detail: Any
                try:
                    detail = upstream.json()
                except Exception:
                    detail = upstream.text
                raise RuntimeError(f"MRP sync HTTP {upstream.status_code}: {detail}")
            data = upstream.json() if upstream.content else {}
            if not isinstance(data, dict):
                data = {"ok": True, "raw": data}
            data["pulled"] = len(items)
            data["attempts"] = attempt
            return data
        except Exception as exc:
            last_exc = exc
            log.warning("mrp_po_sync push attempt %s/%s failed: %s", attempt, _PUSH_MAX_ATTEMPTS, exc)
            if attempt < _PUSH_MAX_ATTEMPTS:
                time.sleep(_PUSH_RETRY_BACKOFF_SEC)
    assert last_exc is not None
    raise last_exc


def _load_details(
    db: Session,
    *,
    detail_ids: list[int] | None = None,
    po_id: int | None = None,
    header_status_mode: str = "active",
    limit: int = 2000,
) -> list[PoDetail]:
    """header_status_mode: active | cancelled | all."""
    q = (
        db.query(PoDetail)
        .options(
            selectinload(PoDetail.po),
            selectinload(PoDetail.color_swatch_recipe),
        )
        .join(PoHeader, PoDetail.po_id == PoHeader.id)
    )
    if detail_ids:
        q = q.filter(PoDetail.id.in_([int(x) for x in detail_ids]))
    elif po_id is not None:
        q = q.filter(PoDetail.po_id == int(po_id))
    else:
        if header_status_mode == "active":
            q = q.filter(PoHeader.status.in_(list(_SYNCABLE_STATUSES)))
        elif header_status_mode == "cancelled":
            q = q.filter(PoHeader.status.in_(list(_CANCELLED_STATUSES)))
        elif header_status_mode == "draft":
            q = q.filter(
                ~PoHeader.status.in_(list(_SYNCABLE_STATUSES | _CANCELLED_STATUSES))
            )
        q = q.order_by(PoDetail.id.desc()).limit(limit)
    return list(q.all())


def sync_po_details_to_mrp(
    db: Session,
    *,
    detail_ids: list[int] | None = None,
    po_id: int | None = None,
    cancelled_detail_ids: list[int] | None = None,
    full: bool = False,
    raise_on_error: bool = False,
) -> dict:
    """Upsert baris PO ke MRP. Default best-effort (tidak raise) untuk hook mutasi ERP."""
    try:
        items: list[dict] = []
        seen: set[int] = set()

        details: list[PoDetail] = []
        if detail_ids or po_id is not None:
            details = _load_details(db, detail_ids=detail_ids, po_id=po_id)
        elif full or not cancelled_detail_ids:
            details = _load_details(db, header_status_mode="active", limit=2000)
            details.extend(_load_details(db, header_status_mode="cancelled", limit=2000))

        for d in details:
            mapped = map_po_detail(d)
            if not mapped:
                continue
            st = ((d.po.status if d.po else "") or "").strip().lower()
            if st not in _SYNCABLE_STATUSES and st not in _CANCELLED_STATUSES:
                continue
            if st in _CANCELLED_STATUSES:
                mapped["cancelled"] = True
            sid = int(d.id)
            items.append(mapped)
            seen.add(sid)

        for sid in cancelled_detail_ids or []:
            try:
                sid_i = int(sid)
            except (TypeError, ValueError):
                continue
            if sid_i in seen:
                continue
            items.append({"source_detail_id": sid_i, "cancelled": True})
            seen.add(sid_i)

        result = _push_items(items)
        result["ok"] = True
        result.setdefault("attempts", 1)
        return result
    except Exception as exc:
        log.warning("mrp_po_sync failed: %s", exc)
        if raise_on_error:
            raise
        return {
            "ok": False,
            "error": str(exc),
            "inserted": 0,
            "updated": 0,
            "total": 0,
            "attempts": _PUSH_MAX_ATTEMPTS,
        }


def try_sync_po_details_to_mrp(db: Session, **kwargs: Any) -> dict:
    """Alias best-effort untuk hook setelah commit PO."""
    kwargs.setdefault("raise_on_error", False)
    return sync_po_details_to_mrp(db, **kwargs)
