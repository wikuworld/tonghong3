"""Packing — antara QC dan Delivery (CR §3.6)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import PackingDetail, PackingHeader, PoDetail, PoHeader, ProductionDetail
from app.schemas import (
    PackingDetailBatchIn,
    PackingDetailEnrichedOut,
    PackingDetailOut,
    PackingDetailUpdate,
    PackingHeaderOut,
)
from app.services.delivery_shipment import lot_number_for_line, so_number_for_line, _has_qc_ok
from app.services.numbering import next_number
from app.services.business_rules import validate_packing_links
from app.routers.auth import get_current_user, require_roles
from app.services.audit import log_change
from app.services.mkt_workflow import sync_mkt_for_packing
from app.services.notifications import create_notification_for_roles

router = APIRouter(tags=["packing"])


class PackingCreate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    production_id: int
    qc_header_id: int
    status: str = "draft"


class PackingHeaderUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    status: Optional[str] = None
    production_id: Optional[int] = None
    qc_header_id: Optional[int] = None


class PackingDetailCreate(BaseModel):
    production_detail_id: Optional[int] = None
    qty_packed: Optional[Decimal] = None
    qty_roll: Optional[int] = None
    qty_pcs: Optional[int] = None
    weight_net: Optional[Decimal] = None


def _enrich_packing_detail(db: Session, d: PackingDetail) -> PackingDetailEnrichedOut:
    pd = db.get(ProductionDetail, d.production_detail_id) if d.production_detail_id else None
    pod = db.get(PoDetail, pd.po_detail_id) if pd and pd.po_detail_id else None
    ph = db.get(PoHeader, pod.po_id) if pod and pod.po_id else None
    return PackingDetailEnrichedOut(
        id=d.id,
        packing_id=d.packing_id,
        production_detail_id=d.production_detail_id,
        qty_packed=float(d.qty_packed) if d.qty_packed is not None else None,
        qty_roll=d.qty_roll,
        qty_pcs=d.qty_pcs,
        weight_net=float(d.weight_net) if d.weight_net is not None else None,
        lot_no=lot_number_for_line(pod, pd),
        so_number=so_number_for_line(ph, pod),
        material_name=(pod.material_name or "").strip() if pod else "",
        qty_actual=float(pd.qty_actual) if pd and pd.qty_actual is not None else None,
    )


@router.get("/packing", response_model=list[PackingHeaderOut])
def list_packing(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Search packing number"),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    _user=Depends(get_current_user),
) -> list[PackingHeader]:
    stmt = select(PackingHeader).order_by(PackingHeader.id.desc()).limit(limit).offset(offset)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(PackingHeader.packing_number.ilike(like))
    rows = db.scalars(stmt).all()
    return rows


@router.post("/packing/{packing_id}/mark-invpl-printed", response_model=PackingHeaderOut)
def mark_invpl_printed(
    packing_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "warehouse")),
) -> PackingHeader:
    row = db.get(PackingHeader, packing_id)
    if not row:
        raise HTTPException(status_code=404, detail="Packing tidak ditemukan")
    before = {"invpl_printed_at": row.invpl_printed_at}
    row.invpl_printed_at = datetime.utcnow()
    log_change(
        db,
        entity_type="packing",
        entity_id=row.id,
        action="mark_invpl_printed",
        before=before,
        after={"invpl_printed_at": row.invpl_printed_at},
        actor=user.username,
    )
    sync_mkt_for_packing(db, packing_id, actor=user.username)
    db.commit()
    db.refresh(row)
    return row


@router.post("/packing", response_model=PackingHeaderOut)
def create_packing(
    body: PackingCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "warehouse")),
) -> PackingHeader:
    validate_packing_links(db, body.production_id, body.qc_header_id)
    num = next_number(db, "PACK", "PACK")
    row = PackingHeader(
        packing_number=num,
        production_id=body.production_id,
        qc_header_id=body.qc_header_id,
        status=body.status,
    )
    db.add(row)
    db.flush()
    log_change(
        db,
        entity_type="packing",
        entity_id=row.id,
        action="create",
        after={"packing_number": row.packing_number, "production_id": row.production_id, "qc_header_id": row.qc_header_id, "status": row.status},
        actor=user.username,
    )
    db.commit()
    db.refresh(row)
    return row


@router.put("/packing/{packing_id}", response_model=PackingHeaderOut)
def update_packing(
    packing_id: int,
    body: PackingHeaderUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "warehouse")),
) -> PackingHeader:
    row = db.get(PackingHeader, packing_id)
    if not row:
        raise HTTPException(status_code=404, detail="Packing tidak ditemukan")
    before = {"status": row.status, "production_id": row.production_id, "qc_header_id": row.qc_header_id}
    data = body.model_dump(exclude_unset=True)
    if "production_id" in data and "qc_header_id" in data:
        validate_packing_links(db, data["production_id"], data["qc_header_id"])
    elif "production_id" in data or "qc_header_id" in data:
        pid = data.get("production_id", row.production_id)
        qid = data.get("qc_header_id", row.qc_header_id)
        if pid and qid:
            validate_packing_links(db, int(pid), int(qid))
    for k, v in data.items():
        setattr(row, k, v)
    if row.status == "done" and before["status"] != "done":
        create_notification_for_roles(
            db,
            ("admin", "warehouse", "marketing"),
            title=f"Packing {row.packing_number} selesai",
            message="Siap diproses ke delivery",
            category="packing",
            entity_type="packing",
            entity_id=row.id,
            route_path="/admin/packing",
            route_query={"packing_id": row.id},
        )
    log_change(
        db,
        entity_type="packing",
        entity_id=row.id,
        action="update",
        before=before,
        after={"status": row.status, "production_id": row.production_id, "qc_header_id": row.qc_header_id},
        actor=user.username,
    )
    db.commit()
    db.refresh(row)
    return row


@router.get("/packing/{packing_id}", response_model=PackingHeaderOut)
def get_packing(
    packing_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> PackingHeader:
    row = db.get(PackingHeader, packing_id)
    if not row:
        raise HTTPException(status_code=404, detail="Packing tidak ditemukan")
    return row


@router.get("/packing/{packing_id}/details", response_model=list[PackingDetailEnrichedOut])
def list_packing_details(
    packing_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> list[PackingDetailEnrichedOut]:
    hdr = db.get(PackingHeader, packing_id)
    if not hdr:
        raise HTTPException(status_code=404, detail="Packing tidak ditemukan")
    rows = db.scalars(
        select(PackingDetail).where(PackingDetail.packing_id == packing_id).order_by(PackingDetail.id.asc())
    ).all()
    return [_enrich_packing_detail(db, d) for d in rows]


@router.get("/packing/{packing_id}/candidate-lines", response_model=list[PackingDetailEnrichedOut])
def list_packing_candidate_lines(
    packing_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> list[PackingDetailEnrichedOut]:
    """Baris produksi QC OK untuk diinput packing list (belum/sudah ada di packing_details)."""
    hdr = db.get(PackingHeader, packing_id)
    if not hdr or not hdr.production_id:
        raise HTTPException(status_code=404, detail="Packing tidak ditemukan")
    existing = {
        int(d.production_detail_id): d
        for d in db.scalars(select(PackingDetail).where(PackingDetail.packing_id == packing_id)).all()
        if d.production_detail_id
    }
    pds = db.scalars(
        select(ProductionDetail)
        .where(ProductionDetail.production_id == hdr.production_id)
        .order_by(ProductionDetail.id.asc())
    ).all()
    out: list[PackingDetailEnrichedOut] = []
    for pd in pds:
        if not _has_qc_ok(db, int(pd.id)):
            continue
        pkd = existing.get(int(pd.id))
        if pkd:
            out.append(_enrich_packing_detail(db, pkd))
        else:
            pod = db.get(PoDetail, pd.po_detail_id) if pd.po_detail_id else None
            ph = db.get(PoHeader, pod.po_id) if pod and pod.po_id else None
            out.append(
                PackingDetailEnrichedOut(
                    id=0,
                    packing_id=packing_id,
                    production_detail_id=int(pd.id),
                    qty_packed=float(pd.qty_actual) if pd.qty_actual is not None else float(pd.qty_planned or 0),
                    qty_roll=None,
                    qty_pcs=None,
                    weight_net=None,
                    lot_no=lot_number_for_line(pod, pd),
                    so_number=so_number_for_line(ph, pod),
                    material_name=(pod.material_name or "").strip() if pod else "",
                    qty_actual=float(pd.qty_actual) if pd.qty_actual is not None else None,
                )
            )
    return out


@router.post("/packing/{packing_id}/details/batch", response_model=list[PackingDetailOut])
def save_packing_details_batch(
    packing_id: int,
    body: PackingDetailBatchIn,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "warehouse")),
) -> list[PackingDetail]:
    hdr = db.get(PackingHeader, packing_id)
    if not hdr:
        raise HTTPException(status_code=404, detail="Packing tidak ditemukan")
    if not body.lines:
        raise HTTPException(status_code=400, detail="Minimal satu baris packing list")
    existing = {
        int(d.production_detail_id): d
        for d in db.scalars(select(PackingDetail).where(PackingDetail.packing_id == packing_id)).all()
        if d.production_detail_id
    }
    saved: list[PackingDetail] = []
    for ln in body.lines:
        pd_id = int(ln.production_detail_id)
        if not _has_qc_ok(db, pd_id):
            raise HTTPException(status_code=400, detail=f"Production detail #{pd_id} belum QC OK")
        row = existing.get(pd_id)
        if row:
            if ln.qty_packed is not None:
                row.qty_packed = ln.qty_packed
            if ln.qty_roll is not None:
                row.qty_roll = ln.qty_roll
            if ln.qty_pcs is not None:
                row.qty_pcs = ln.qty_pcs
            if ln.weight_net is not None:
                row.weight_net = ln.weight_net
        else:
            row = PackingDetail(
                packing_id=packing_id,
                production_detail_id=pd_id,
                qty_packed=ln.qty_packed,
                qty_roll=ln.qty_roll,
                qty_pcs=ln.qty_pcs,
                weight_net=ln.weight_net,
            )
            db.add(row)
            existing[pd_id] = row
        saved.append(row)
    db.flush()
    log_change(
        db,
        entity_type="packing",
        entity_id=packing_id,
        action="batch_details",
        after={"line_count": len(body.lines)},
        actor=user.username,
    )
    db.commit()
    for row in saved:
        db.refresh(row)
    return saved


@router.post("/packing/{packing_id}/details", response_model=PackingDetailOut)
def add_packing_detail(
    packing_id: int,
    body: PackingDetailCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "warehouse")),
) -> PackingDetail:
    hdr = db.get(PackingHeader, packing_id)
    if not hdr:
        raise HTTPException(status_code=404, detail="Packing tidak ditemukan")
    if body.production_detail_id and not _has_qc_ok(db, int(body.production_detail_id)):
        raise HTTPException(status_code=400, detail="Hanya baris QC OK yang boleh dipacking")
    d = PackingDetail(
        packing_id=packing_id,
        production_detail_id=body.production_detail_id,
        qty_packed=body.qty_packed,
        qty_roll=body.qty_roll,
        qty_pcs=body.qty_pcs,
        weight_net=body.weight_net,
    )
    db.add(d)
    db.flush()
    log_change(
        db,
        entity_type="packing_line",
        entity_id=d.id,
        action="create",
        after={"packing_id": packing_id, "production_detail_id": d.production_detail_id, "qty_packed": d.qty_packed},
        actor=user.username,
    )
    db.commit()
    db.refresh(d)
    return d


@router.put("/packing-detail/{detail_id}", response_model=PackingDetailOut)
def update_packing_detail(
    detail_id: int,
    body: PackingDetailUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "warehouse")),
) -> PackingDetail:
    row = db.get(PackingDetail, detail_id)
    if not row:
        raise HTTPException(status_code=404, detail="Baris packing tidak ditemukan")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/packing-detail/{detail_id}")
def delete_packing_detail(
    detail_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "warehouse")),
) -> dict:
    row = db.get(PackingDetail, detail_id)
    if not row:
        raise HTTPException(status_code=404, detail="Baris packing tidak ditemukan")
    db.delete(row)
    db.commit()
    return {"status": "ok"}
