"""Packing — antara QC dan Delivery (CR §3.6)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import PackingDetail, PackingHeader
from app.schemas import row_to_dict
from app.services.numbering import next_number
from app.services.business_rules import validate_packing_links

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


@router.get("/packing")
def list_packing(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.scalars(select(PackingHeader).order_by(PackingHeader.id.desc())).all()
    return [row_to_dict(r) for r in rows]


@router.post("/packing/{packing_id}/mark-invpl-printed")
def mark_invpl_printed(packing_id: int, db: Session = Depends(get_db)) -> dict:
    row = db.get(PackingHeader, packing_id)
    if not row:
        raise HTTPException(status_code=404, detail="Packing tidak ditemukan")
    row.invpl_printed_at = datetime.utcnow()
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.post("/packing")
def create_packing(body: PackingCreate, db: Session = Depends(get_db)) -> dict:
    validate_packing_links(db, body.production_id, body.qc_header_id)
    num = next_number(db, "PACK", "PACK")
    row = PackingHeader(
        packing_number=num,
        production_id=body.production_id,
        qc_header_id=body.qc_header_id,
        status=body.status,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.put("/packing/{packing_id}")
def update_packing(
    packing_id: int, body: PackingHeaderUpdate, db: Session = Depends(get_db)
) -> dict:
    row = db.get(PackingHeader, packing_id)
    if not row:
        raise HTTPException(status_code=404, detail="Packing tidak ditemukan")
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
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.get("/packing/{packing_id}")
def get_packing(packing_id: int, db: Session = Depends(get_db)) -> dict:
    row = db.get(PackingHeader, packing_id)
    if not row:
        raise HTTPException(status_code=404, detail="Packing tidak ditemukan")
    return row_to_dict(row)


@router.post("/packing/{packing_id}/details")
def add_packing_detail(
    packing_id: int, body: PackingDetailCreate, db: Session = Depends(get_db)
) -> dict:
    hdr = db.get(PackingHeader, packing_id)
    if not hdr:
        raise HTTPException(status_code=404, detail="Packing tidak ditemukan")
    d = PackingDetail(
        packing_id=packing_id,
        production_detail_id=body.production_detail_id,
        qty_packed=body.qty_packed,
    )
    db.add(d)
    db.commit()
    db.refresh(d)
    return row_to_dict(d)
