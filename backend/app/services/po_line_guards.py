"""Kunci identitas baris SO yang sudah produksi / WIP MRP."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import PoDetail, ProductionDetail
from app.services.mrp_po_alloc import fetch_mrp_alloc_by_detail_ids
from app.services.po_delivery_balance import sum_delivered_qty_for_po_detail

PO_LINE_IDENTITY_FIELDS = frozenset(
    {
        "master_item_id",
        "thi_line_ref",
        "material_name",
        "color",
        "color_family",
        "thickness_min",
        "thickness_max",
        "thickness_text",
        "emboss",
        "vir_softness_type",
        "softness",
        "color_reference",
        "color_standard",
        "backing",
        "style_article",
        "model",
        "system_reference",
        "color_swatch_recipe_id",
    }
)

_LOCK_PRODUCTION = "Baris sudah masuk produksi — identitas dan lot tidak dapat diubah"
_LOCK_WIP = "Baris sudah masuk WIP/rencana MRP — identitas dan lot tidak dapat diubah"


def _dec(v: Any) -> Decimal:
    if v is None or v == "":
        return Decimal(0)
    try:
        return Decimal(str(v))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal(0)


def _same(old: Any, new: Any) -> bool:
    if old is None and new is None:
        return True
    if isinstance(old, Decimal) or isinstance(new, Decimal) or isinstance(old, (int, float)) or isinstance(new, (int, float)):
        return _dec(old) == _dec(new)
    if isinstance(old, str) or isinstance(new, str):
        return str(old or "").strip() == str(new or "").strip()
    return old == new


def _mrp_lock_reason(alloc: dict[str, str] | None) -> str | None:
    if not alloc:
        return None
    if _dec(alloc.get("mrp_qty_wip")) > 0:
        return _LOCK_WIP
    if _dec(alloc.get("mrp_qty_processed")) > 0:
        return _LOCK_WIP
    return None


def _production_qty_floor(db: Session, detail_id: int) -> Decimal:
    rows = list(
        db.scalars(select(ProductionDetail).where(ProductionDetail.po_detail_id == detail_id)).all()
    )
    total = Decimal(0)
    for pd in rows:
        total += max(_dec(pd.qty_actual), _dec(pd.qty_planned))
    return total


def po_detail_lock_state(
    db: Session,
    detail_id: int,
    *,
    alloc: dict[str, str] | None = None,
) -> tuple[bool, str | None]:
    in_prod = db.scalars(
        select(ProductionDetail.id).where(ProductionDetail.po_detail_id == detail_id).limit(1)
    ).first()
    if in_prod is not None:
        return True, _LOCK_PRODUCTION
    if alloc is None:
        found = fetch_mrp_alloc_by_detail_ids([detail_id])
        alloc = found.get(int(detail_id))
    reason = _mrp_lock_reason(alloc)
    if reason:
        return True, reason
    return False, None


def attach_po_line_locks(db: Session, details: list) -> None:
    ids = [int(d.id) for d in details if getattr(d, "id", None) is not None]
    if not ids:
        return
    prod_ids = {
        int(x)
        for x in db.scalars(
            select(ProductionDetail.po_detail_id).where(ProductionDetail.po_detail_id.in_(ids))
        ).all()
        if x is not None
    }
    alloc_map = fetch_mrp_alloc_by_detail_ids(ids)
    for row in details:
        if getattr(row, "id", None) is None:
            row.line_locked = False
            row.line_lock_reason = None
            continue
        did = int(row.id)
        if did in prod_ids:
            row.line_locked = True
            row.line_lock_reason = _LOCK_PRODUCTION
            continue
        reason = _mrp_lock_reason(alloc_map.get(did))
        row.line_locked = bool(reason)
        row.line_lock_reason = reason


def qty_floor_for_po_detail(db: Session, detail_id: int, *, alloc: dict[str, str] | None = None) -> Decimal:
    delivered = sum_delivered_qty_for_po_detail(db, detail_id)
    prod_qty = _production_qty_floor(db, detail_id)
    if alloc is None:
        found = fetch_mrp_alloc_by_detail_ids([detail_id])
        alloc = found.get(int(detail_id)) or {}
    wip = _dec((alloc or {}).get("mrp_qty_wip"))
    processed = _dec((alloc or {}).get("mrp_qty_processed"))
    return max(delivered, prod_qty, wip, processed)


def assert_po_detail_update_allowed(db: Session, row: PoDetail, data: dict[str, Any]) -> None:
    locked, reason = po_detail_lock_state(db, int(row.id))
    if not locked:
        if "quantity_order" in data:
            floor = qty_floor_for_po_detail(db, int(row.id))
            if _dec(data.get("quantity_order")) < floor:
                raise HTTPException(
                    status_code=400,
                    detail=f"Qty tidak boleh kurang dari {floor} (sudah produksi/kirim)",
                )
        return

    changed = [k for k in PO_LINE_IDENTITY_FIELDS if k in data and not _same(getattr(row, k, None), data.get(k))]
    if changed:
        raise HTTPException(status_code=400, detail=reason or _LOCK_PRODUCTION)

    if "quantity_order" in data:
        floor = qty_floor_for_po_detail(db, int(row.id))
        new_qty = _dec(data.get("quantity_order"))
        if new_qty < floor:
            raise HTTPException(
                status_code=400,
                detail=f"Qty tidak boleh kurang dari {floor} (sudah produksi/WIP/kirim)",
            )


def assert_po_detail_not_in_wip(db: Session, detail_id: int, *, action: str = "menghapus") -> None:
    locked, reason = po_detail_lock_state(db, detail_id)
    if locked:
        raise HTTPException(
            status_code=400,
            detail=reason or f"Tidak dapat {action} item yang sudah masuk produksi/WIP",
        )
