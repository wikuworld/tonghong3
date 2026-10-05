"""Write-back Production/QC mirror dari packing/WIP MRP → ERP."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from mrp_api.models import (
    PoDetail,
    PoHeader,
    ProductionDetail,
    ProductionOrder,
)
from mrp_api.services.audit import log_change
from mrp_api.services.numbering import next_number


@dataclass
class ProductionBridgeResult:
    production_id: int
    production_detail_id: int
    production_number: str | None
    qc_header_id: int | None
    created: bool
    finished: bool


def _dec(v: Any) -> Decimal:
    if v is None:
        return Decimal("0")
    if isinstance(v, Decimal):
        return v
    return Decimal(str(v))


def upsert_production_mirror(
    db: Session,
    *,
    source_detail_id: int,
    kode_wip: str,
    mrp_packing_id: int | None = None,
    qty_planned: Decimal | float | int | None = None,
    qty_actual: Decimal | float | int | None = None,
    finish: bool = False,
    actor: str | None = None,
) -> ProductionBridgeResult:
    """Idempotent: satu ProductionDetail per kode_wip (lot_number)."""
    kode_wip = (kode_wip or "").strip()
    if not kode_wip:
        raise HTTPException(status_code=400, detail="kode_wip wajib")
    try:
        sid = int(source_detail_id)
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail="source_detail_id wajib") from e

    pod = db.get(PoDetail, sid)
    if not pod:
        raise HTTPException(status_code=400, detail=f"po_details #{sid} tidak ditemukan")
    ph = db.get(PoHeader, pod.po_id) if pod.po_id else None
    if not ph:
        raise HTTPException(status_code=400, detail="PO header tidak ditemukan")
    if (ph.status or "").lower() in {"cancelled", "canceled", "void"}:
        raise HTTPException(status_code=400, detail=f"PO {ph.po_number} berstatus {ph.status}")

    existing_pd = db.scalars(
        select(ProductionDetail).where(ProductionDetail.lot_number == kode_wip).limit(1)
    ).first()

    planned = _dec(qty_planned if qty_planned is not None else pod.quantity_order)
    actual = _dec(qty_actual) if qty_actual is not None else None

    created = False
    if existing_pd:
        pd = existing_pd
        pr = db.get(ProductionOrder, pd.production_id) if pd.production_id else None
        if not pr:
            raise HTTPException(status_code=500, detail="Production order mirror hilang")
        if planned > 0:
            pd.qty_planned = planned
        if actual is not None:
            pd.qty_actual = actual
        if finish:
            pd.status = "completed"
            pd.qty_actual = actual if actual is not None else (pd.qty_actual or pd.qty_planned)
            if (pr.status or "").lower() not in {"completed", "done"}:
                pr.status = "in_progress"
    else:
        pr = db.scalars(
            select(ProductionOrder)
            .where(
                ProductionOrder.po_id == ph.id,
                ProductionOrder.production_number.like("MRP-%"),
            )
            .order_by(ProductionOrder.id.desc())
            .limit(1)
        ).first()
        if not pr:
            num = next_number(db, "PRD", "PRD")
            pr = ProductionOrder(
                production_number=f"MRP-{num}"[:100],
                po_id=ph.id,
                start_date=date.today(),
                status="in_progress",
            )
            db.add(pr)
            db.flush()
            if (ph.status or "").lower() == "confirmed":
                ph.status = "production"
            created = True

        pd = ProductionDetail(
            production_id=pr.id,
            po_detail_id=sid,
            qty_planned=planned,
            qty_actual=actual if actual is not None else (planned if finish else None),
            lot_number=kode_wip,
            batch_number=str(mrp_packing_id) if mrp_packing_id else None,
            status="completed" if finish else "in_progress",
        )
        db.add(pd)
        db.flush()
        created = True

    qc_header_id: Optional[int] = None

    log_change(
        db,
        entity_type="production",
        entity_id=pr.id,
        action="mrp_production_mirror",
        after={
            "kode_wip": kode_wip,
            "source_detail_id": sid,
            "production_detail_id": pd.id,
            "finish": finish,
            "mrp_packing_id": mrp_packing_id,
        },
        actor=actor or "system",
    )
    db.flush()
    return ProductionBridgeResult(
        production_id=int(pr.id),
        production_detail_id=int(pd.id),
        production_number=pr.production_number,
        qc_header_id=qc_header_id,
        created=created,
        finished=bool(finish),
    )
