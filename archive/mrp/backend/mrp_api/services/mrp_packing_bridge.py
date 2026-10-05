"""Packing MRP finish → packing ERP siap kirim (tanpa Surat Jalan)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from mrp_api.models import (
    PackingDetail,
    PackingHeader,
    ProductionDetail,
    QcDetail,
    QcHeader,
)
from mrp_api.services.audit import log_change
from mrp_api.services.numbering import next_number


@dataclass
class ErpPackingReadyResult:
    packing_id: int
    packing_number: str | None
    production_id: int
    created: bool
    qc_header_id: int | None


def _dec(v: Any) -> Decimal:
    if v is None:
        return Decimal("0")
    if isinstance(v, Decimal):
        return v
    return Decimal(str(v))


def kode_packing_from_erp(pk: PackingHeader | None) -> str:
    num = ((pk.packing_number if pk else "") or "").strip()
    if num.upper().startswith("MRP-"):
        return num[4:].strip()
    return num


def _ensure_qc_ok(
    db: Session,
    *,
    production_id: int,
    production_detail_id: int,
    actor: str | None,
) -> int | None:
    existing = db.scalars(
        select(QcDetail).where(
            and_(
                QcDetail.production_detail_id == int(production_detail_id),
                QcDetail.is_ok.is_(True),
            )
        )
    ).first()
    if existing:
        return int(existing.qc_id) if existing.qc_id else None

    qc = db.scalars(
        select(QcHeader).where(QcHeader.production_id == int(production_id)).limit(1)
    ).first()
    if not qc:
        qc = QcHeader(
            qc_number=next_number(db, "QC", "QC"),
            production_id=int(production_id),
            qc_date=date.today(),
            operator_name=actor or "mrp",
        )
        db.add(qc)
        db.flush()
    db.add(
        QcDetail(
            qc_id=qc.id,
            production_detail_id=int(production_detail_id),
            result="OK",
            is_ok=True,
        )
    )
    db.flush()
    return int(qc.id)


def ensure_erp_packing_from_mrp_finish(
    db: Session,
    *,
    mrp_packing_id: int,
    kode_packing: str | None,
    production_id: int,
    lines: list[tuple[int, Decimal | float | int | None]],
    actor: str | None = None,
) -> ErpPackingReadyResult:
    """Idempotent: PackingHeader done + detail + QC OK. Tidak membuat Delivery."""
    if not mrp_packing_id:
        raise HTTPException(status_code=400, detail="mrp_packing_id wajib")
    if not production_id:
        raise HTTPException(status_code=400, detail="production_id wajib")
    usable = [(int(pd_id), _dec(qty)) for pd_id, qty in (lines or []) if pd_id]
    if not usable:
        raise HTTPException(status_code=400, detail="Packing finish tanpa baris production detail")

    existing = db.scalars(
        select(PackingHeader)
        .where(PackingHeader.mrp_packing_id == int(mrp_packing_id))
        .order_by(PackingHeader.id.desc())
        .limit(1)
    ).first()

    created = False
    kode = (kode_packing or "").strip()
    packing_number = f"MRP-{kode}"[:100] if kode else None
    if existing:
        pk = existing
        pk.production_id = int(production_id)
        pk.status = "done"
        pk.source = "mrp"
        if packing_number and not (pk.packing_number or "").strip():
            pk.packing_number = packing_number
    else:
        if packing_number:
            clash = db.scalars(
                select(PackingHeader).where(PackingHeader.packing_number == packing_number).limit(1)
            ).first()
            if clash:
                packing_number = next_number(db, "PACK", "PACK")
        else:
            packing_number = next_number(db, "PACK", "PACK")
        pk = PackingHeader(
            packing_number=packing_number,
            production_id=int(production_id),
            status="done",
            source="mrp",
            mrp_packing_id=int(mrp_packing_id),
        )
        db.add(pk)
        db.flush()
        created = True

    qc_id: Optional[int] = None
    seen_pd: set[int] = set()
    for pd_id, qty in usable:
        pd = db.get(ProductionDetail, pd_id)
        if not pd:
            raise HTTPException(status_code=400, detail=f"Production detail #{pd_id} tidak ditemukan")
        if pd_id in seen_pd:
            continue
        seen_pd.add(pd_id)
        qc_id = _ensure_qc_ok(
            db,
            production_id=int(production_id),
            production_detail_id=pd_id,
            actor=actor,
        )
        pkd = db.scalars(
            select(PackingDetail).where(
                and_(
                    PackingDetail.packing_id == pk.id,
                    PackingDetail.production_detail_id == pd_id,
                )
            )
        ).first()
        packed = qty if qty > 0 else _dec(pd.qty_actual if pd.qty_actual is not None else pd.qty_planned)
        if pkd:
            if packed > 0:
                pkd.qty_packed = packed
        else:
            db.add(
                PackingDetail(
                    packing_id=pk.id,
                    production_detail_id=pd_id,
                    qty_packed=packed if packed > 0 else None,
                )
            )
    if qc_id:
        pk.qc_header_id = qc_id
    db.flush()
    log_change(
        db,
        entity_type="packing",
        entity_id=pk.id,
        action="mrp_packing_ready",
        after={
            "mrp_packing_id": int(mrp_packing_id),
            "kode_packing": kode,
            "production_id": int(production_id),
            "line_count": len(seen_pd),
        },
        actor=actor or "system",
    )
    db.flush()
    return ErpPackingReadyResult(
        packing_id=int(pk.id),
        packing_number=pk.packing_number,
        production_id=int(production_id),
        created=created,
        qc_header_id=qc_id,
    )
