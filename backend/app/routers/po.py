from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models import PoDetail, PoHeader
from app.services.audit import log_change
from app.services.numbering import next_number
from app.schemas import (
    PoDetailCreate,
    PoDetailOut,
    PoDetailUpdate,
    PoHeaderCreate,
    PoHeaderOut,
    PoHeaderUpdate,
)
from app.services.business_rules import validate_po_status_transition
from app.services.mkt_workflow import (
    MKT_STAGES_ORDER,
    apply_mkt_stage,
    next_mkt_stage,
    validate_mkt_advance,
)

router = APIRouter(tags=["po"])


def _detail_loaded(db: Session, detail_id: int) -> Optional[PoDetail]:
    return db.scalars(
        select(PoDetail)
        .options(selectinload(PoDetail.delivery_schedules))
        .where(PoDetail.id == detail_id)
    ).first()


@router.get("/po/mkt-workflow-stages")
def mkt_workflow_stages() -> dict:
    return {"stages": list(MKT_STAGES_ORDER)}


@router.get("/po", response_model=list[PoHeaderOut])
def list_po(
    mkt_workflow_stage: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> list[PoHeader]:
    stmt = select(PoHeader).order_by(PoHeader.id.desc())
    if mkt_workflow_stage:
        stmt = stmt.where(PoHeader.mkt_workflow_stage == mkt_workflow_stage)
    return list(db.scalars(stmt).all())


@router.post("/po/{po_id}/mkt-workflow/advance", response_model=PoHeaderOut)
def advance_mkt_workflow(po_id: int, db: Session = Depends(get_db)) -> PoHeader:
    row = db.get(PoHeader, po_id)
    if not row:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")
    nxt = next_mkt_stage(row.mkt_workflow_stage)
    if not nxt:
        raise HTTPException(status_code=400, detail="PO sudah di tahap akhir alur MKT")
    validate_mkt_advance(db, po_id, nxt)
    apply_mkt_stage(db, po_id, nxt)
    db.commit()
    db.refresh(row)
    return row


@router.post("/po", response_model=PoHeaderOut)
def create_po(body: PoHeaderCreate, db: Session = Depends(get_db)) -> PoHeader:
    data = body.model_dump(exclude_unset=True)
    if not data.get("po_number"):
        data["po_number"] = next_number(db, "SO", "SO")
    row = PoHeader(**data)
    db.add(row)
    db.flush()
    log_change(
        db,
        entity_type="sales_order",
        entity_id=row.id,
        action="create",
        after={"po_number": row.po_number, "status": row.status},
    )
    db.commit()
    db.refresh(row)
    return row


@router.get("/po/{po_id}", response_model=PoHeaderOut)
def get_po(po_id: int, db: Session = Depends(get_db)) -> PoHeader:
    row = db.get(PoHeader, po_id)
    if not row:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")
    return row


@router.get("/po/{po_id}/details", response_model=list[PoDetailOut])
def list_po_details(po_id: int, db: Session = Depends(get_db)) -> list[PoDetail]:
    if not db.get(PoHeader, po_id):
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")
    rows = db.scalars(
        select(PoDetail)
        .options(selectinload(PoDetail.delivery_schedules))
        .where(PoDetail.po_id == po_id)
        .order_by(PoDetail.id.asc())
    ).all()
    return list(rows)


@router.put("/po/{po_id}", response_model=PoHeaderOut)
def update_po(po_id: int, body: PoHeaderUpdate, db: Session = Depends(get_db)) -> PoHeader:
    row = db.get(PoHeader, po_id)
    if not row:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")
    data = body.model_dump(exclude_unset=True)
    if "status" in data:
        validate_po_status_transition(row.status, data["status"])
    for k, v in data.items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/po/{po_id}")
def delete_po(po_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    row = db.get(PoHeader, po_id)
    if not row:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")
    db.delete(row)
    db.commit()
    return {"status": "deleted"}


@router.post("/po/{po_id}/details", response_model=PoDetailOut)
def add_po_detail(
    po_id: int, body: PoDetailCreate, db: Session = Depends(get_db)
) -> PoDetail:
    po = db.get(PoHeader, po_id)
    if not po:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")
    row = PoDetail(po_id=po_id, **body.model_dump(exclude_unset=True))
    db.add(row)
    db.commit()
    out = _detail_loaded(db, row.id)
    return out or row


@router.put("/po-detail/{detail_id}", response_model=PoDetailOut)
def update_po_detail(
    detail_id: int, body: PoDetailUpdate, db: Session = Depends(get_db)
) -> PoDetail:
    row = db.get(PoDetail, detail_id)
    if not row:
        raise HTTPException(status_code=404, detail="Detail PO tidak ditemukan")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.commit()
    out = _detail_loaded(db, detail_id)
    return out or row


@router.delete("/po-detail/{detail_id}")
def delete_po_detail(detail_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    row = db.get(PoDetail, detail_id)
    if not row:
        raise HTTPException(status_code=404, detail="Detail PO tidak ditemukan")
    db.delete(row)
    db.commit()
    return {"status": "deleted"}
