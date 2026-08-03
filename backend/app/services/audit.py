"""Audit trail (CR §3.x mandatory audit)."""

from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models import AuditLog


def _audit_scalar(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def _delivery_schedules_snapshot(row: Any) -> list[dict[str, Any]]:
    schedules = list(getattr(row, "delivery_schedules", None) or [])
    schedules.sort(key=lambda s: int(getattr(s, "sequence_no", 0) or 0))
    out: list[dict[str, Any]] = []
    for s in schedules:
        out.append(
            {
                "sequence_no": getattr(s, "sequence_no", None),
                "qty": _audit_scalar(getattr(s, "qty", None)),
                "delivery_date": _audit_scalar(getattr(s, "delivery_date", None)),
            }
        )
    return out


def po_detail_audit_snapshot(row: Any, *, include_schedules: bool = False) -> dict[str, Any]:
    """Snapshot field bisnis baris PO untuk CREATE/UPDATE/DELETE audit."""
    snap: dict[str, Any] = {
        "po_id": getattr(row, "po_id", None),
        "master_item_id": getattr(row, "master_item_id", None),
        "thi_line_ref": getattr(row, "thi_line_ref", None),
        "material_name": getattr(row, "material_name", None),
        "color": getattr(row, "color", None),
        "color_family": getattr(row, "color_family", None),
        "color_reference": getattr(row, "color_reference", None),
        "color_standard": getattr(row, "color_standard", None),
        "thickness_text": getattr(row, "thickness_text", None),
        "thickness_min": _audit_scalar(getattr(row, "thickness_min", None)),
        "thickness_max": _audit_scalar(getattr(row, "thickness_max", None)),
        "emboss": getattr(row, "emboss", None),
        "softness": getattr(row, "softness", None),
        "vir_softness_type": getattr(row, "vir_softness_type", None),
        "backing": getattr(row, "backing", None),
        "quantity_order": _audit_scalar(getattr(row, "quantity_order", None)),
        "unit_price": _audit_scalar(getattr(row, "unit_price", None)),
        "style_article": getattr(row, "style_article", None),
        "model": getattr(row, "model", None),
        "line_etd": _audit_scalar(getattr(row, "line_etd", None)),
        "detail_remark": getattr(row, "detail_remark", None),
        "color_swatch_recipe_id": getattr(row, "color_swatch_recipe_id", None),
    }
    if include_schedules:
        snap["delivery_schedules"] = _delivery_schedules_snapshot(row)
    return snap


def mark_po_item_revised(db: Session, po_id: Optional[int], *, kind: str) -> None:
    """Tandai header SO bahwa ada baris item di-update atau di-delete."""
    if po_id is None:
        return
    kind_norm = (kind or "").strip().lower()
    if kind_norm not in {"update", "delete"}:
        return
    from app.models import PoHeader

    po = db.get(PoHeader, int(po_id))
    if not po:
        return
    po.item_revised_at = datetime.utcnow()
    if kind_norm == "delete":
        po.item_revised_has_delete = True
    else:
        po.item_revised_has_update = True


def log_change(
    db: Session,
    *,
    entity_type: str,
    entity_id: Optional[int],
    action: str,
    before: Optional[dict[str, Any]] = None,
    after: Optional[dict[str, Any]] = None,
    actor: str = "system",
) -> None:
    row = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        payload_before=json.dumps(before, default=str) if before is not None else None,
        payload_after=json.dumps(after, default=str) if after is not None else None,
        actor=actor,
    )
    db.add(row)
