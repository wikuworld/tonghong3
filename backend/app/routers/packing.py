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
from app.models import PackingDetail, PackingHeader
from app.schemas import PackingDetailOut, PackingHeaderOut
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
    d = PackingDetail(
        packing_id=packing_id,
        production_detail_id=body.production_detail_id,
        qty_packed=body.qty_packed,
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
