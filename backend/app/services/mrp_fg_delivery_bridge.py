"""Bridge Gudang FG OUT (MRP) → Packing stub + Delivery draft ERP."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    DeliveryDetail,
    DeliveryHeader,
    PackingHeader,
    PoDetail,
    PoHeader,
    ProductionDetail,
)
from app.services.audit import log_change
from app.services.numbering import next_number
from app.services.po_delivery_balance import (
    sync_po_detail_balance_qty,
    validate_delivery_qty_against_po_balance,
)


@dataclass
class BridgeLine:
    source_detail_id: int
    qty_out: Decimal
    qty_roll: int | None = None
    qty_pcs: int | None = None
    weight: Decimal | None = None


@dataclass
class BridgeResult:
    delivery_id: int
    delivery_number: str | None
    packing_id: int
    packing_number: str | None
    created: bool
    line_count: int
    po_detail_ids: list[int] | None = None


def _dec(v: Any) -> Decimal:
    if v is None:
        return Decimal("0")
    if isinstance(v, Decimal):
        return v
    return Decimal(str(v))


def _parse_lines(raw_lines: list[dict[str, Any]]) -> list[BridgeLine]:
    lines: list[BridgeLine] = []
    for raw in raw_lines or []:
        try:
            sid = int(raw.get("source_detail_id"))
        except (TypeError, ValueError):
            continue
        qty = _dec(raw.get("qty_out") if raw.get("qty_out") is not None else raw.get("qty_sq"))
        if qty <= 0:
            continue
        qty_roll = raw.get("qty_roll")
        qty_pcs = raw.get("qty_pcs")
        try:
            qty_roll = int(qty_roll) if qty_roll is not None else None
        except (TypeError, ValueError):
            qty_roll = None
        try:
            qty_pcs = int(qty_pcs) if qty_pcs is not None else None
        except (TypeError, ValueError):
            qty_pcs = None
        weight = raw.get("weight")
        weight_dec = _dec(weight) if weight is not None else None
        lines.append(
            BridgeLine(
                source_detail_id=sid,
                qty_out=qty,
                qty_roll=qty_roll,
                qty_pcs=qty_pcs,
                weight=weight_dec if weight_dec and weight_dec > 0 else None,
            )
        )
    return lines


def bridge_fg_out_to_delivery(
    db: Session,
    *,
    mrp_fg_id: int,
    mrp_packing_id: int | None,
    kode_packing: str | None,
    customer_name: str | None,
    lines: list[dict[str, Any]],
    actor: str | None = None,
    keterangan: str | None = None,
) -> BridgeResult:
    """Buat/temukan packing stub + delivery draft untuk satu FG OUT MRP (idempotent)."""
    if not mrp_fg_id:
        raise HTTPException(status_code=400, detail="mrp_fg_id wajib")

    existing = db.scalars(
        select(DeliveryHeader).where(DeliveryHeader.mrp_fg_id == int(mrp_fg_id)).limit(1)
    ).first()
    if existing:
        pk = db.get(PackingHeader, existing.packing_id) if existing.packing_id else None
        return BridgeResult(
            delivery_id=int(existing.id),
            delivery_number=existing.delivery_number,
            packing_id=int(existing.packing_id or 0),
            packing_number=pk.packing_number if pk else None,
            created=False,
            line_count=0,
        )

    existing_pk = db.scalars(
        select(PackingHeader).where(PackingHeader.mrp_fg_id == int(mrp_fg_id)).limit(1)
    ).first()
    if existing_pk:
        existing_dh = db.scalars(
            select(DeliveryHeader).where(DeliveryHeader.packing_id == existing_pk.id).limit(1)
        ).first()
        if existing_dh:
            return BridgeResult(
                delivery_id=int(existing_dh.id),
                delivery_number=existing_dh.delivery_number,
                packing_id=int(existing_pk.id),
                packing_number=existing_pk.packing_number,
                created=False,
                line_count=0,
            )

    parsed = _parse_lines(lines)
    if not parsed:
        raise HTTPException(
            status_code=400,
            detail=(
                "Tidak ada baris PO dengan source_detail_id untuk bridge. "
                "Jalankan Sync PO lalu pastikan packing/rencana terhubung ke master PO."
            ),
        )

    # Aggregate qty per po_detail
    qty_by_pod: dict[int, BridgeLine] = {}
    for ln in parsed:
        prev = qty_by_pod.get(ln.source_detail_id)
        if prev is None:
            qty_by_pod[ln.source_detail_id] = ln
        else:
            prev.qty_out += ln.qty_out
            if ln.qty_roll:
                prev.qty_roll = (prev.qty_roll or 0) + ln.qty_roll
            if ln.qty_pcs:
                prev.qty_pcs = (prev.qty_pcs or 0) + ln.qty_pcs

    customer_id: Optional[int] = None
    resolved: list[tuple[PoDetail, BridgeLine]] = []
    for sid, ln in qty_by_pod.items():
        pod = db.get(PoDetail, sid)
        if not pod:
            raise HTTPException(
                status_code=400,
                detail=f"po_details #{sid} tidak ditemukan (source_detail_id)",
            )
        ph = db.get(PoHeader, pod.po_id) if pod.po_id else None
        if ph and (ph.status or "").lower() in {"cancelled", "canceled", "void"}:
            raise HTTPException(
                status_code=400,
                detail=f"PO {ph.po_number or ph.id} berstatus {ph.status}",
            )
        if customer_id is None and ph and ph.customer_id:
            customer_id = int(ph.customer_id)
        validate_delivery_qty_against_po_balance(
            db,
            po_detail_id=int(pod.id),
            qty=ln.qty_out,
        )
        resolved.append((pod, ln))

    packing_number = next_number(db, "PACK", "PACK")
    if kode_packing:
        packing_number = f"MRP-{kode_packing}"[:100]
        clash = db.scalars(
            select(PackingHeader).where(PackingHeader.packing_number == packing_number).limit(1)
        ).first()
        if clash:
            packing_number = next_number(db, "PACK", "PACK")

    pk = PackingHeader(
        packing_number=packing_number,
        production_id=None,
        qc_header_id=None,
        status="done",
        source="mrp",
        mrp_packing_id=int(mrp_packing_id) if mrp_packing_id else None,
        mrp_fg_id=int(mrp_fg_id),
    )
    db.add(pk)
    db.flush()

    delivery_number = next_number(db, "DEL", "DEL")
    dest = (keterangan or "").strip() or None
    if customer_name and not dest:
        dest = f"MRP FG OUT — {customer_name}"
    elif customer_name and dest:
        dest = f"{dest} ({customer_name})"

    hdr = DeliveryHeader(
        delivery_number=delivery_number,
        customer_id=customer_id,
        packing_id=pk.id,
        delivery_date=date.today(),
        delivery_type="production",
        delivery_zone="outtown",
        destination=dest,
        status="draft",
        mrp_fg_id=int(mrp_fg_id),
    )
    db.add(hdr)
    db.flush()

    touched_pods: list[int] = []
    for pod, ln in resolved:
        pd_mirror = db.scalars(
            select(ProductionDetail)
            .where(ProductionDetail.po_detail_id == int(pod.id))
            .order_by(ProductionDetail.id.desc())
            .limit(1)
        ).first()
        db.add(
            DeliveryDetail(
                delivery_id=hdr.id,
                production_detail_id=int(pd_mirror.id) if pd_mirror else None,
                packing_detail_id=None,
                po_detail_id=int(pod.id),
                qty=ln.qty_out,
                qty_roll=ln.qty_roll,
                qty_pcs=ln.qty_pcs,
                weight=ln.weight,
            )
        )
        touched_pods.append(int(pod.id))
    db.flush()
    for pod_id in touched_pods:
        sync_po_detail_balance_qty(db, pod_id)

    log_change(
        db,
        entity_type="delivery",
        entity_id=hdr.id,
        action="create_from_mrp_fg_out",
        after={
            "mrp_fg_id": mrp_fg_id,
            "mrp_packing_id": mrp_packing_id,
            "packing_id": pk.id,
            "line_count": len(resolved),
            "kode_packing": kode_packing,
        },
        actor=actor or "system",
    )
    db.flush()
    return BridgeResult(
        delivery_id=int(hdr.id),
        delivery_number=hdr.delivery_number,
        packing_id=int(pk.id),
        packing_number=pk.packing_number,
        created=True,
        line_count=len(resolved),
        po_detail_ids=list(touched_pods),
    )
