from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import PoDetail, PoHeader, ProductionDetail, ProductionOrder
from app.services.numbering import next_number
from app.schemas import (
    ProductionCreate,
    ProductionDetailCreate,
    ProductionDetailUpdate,
    row_to_dict,
)
from app.routers.auth import get_current_user, require_roles
from app.services.audit import log_change
from app.services.notifications import create_notification_for_roles

router = APIRouter(tags=["production"])


def _require_po_confirmed(po: PoHeader | None) -> None:
    if not po:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")
    if po.status not in ("confirmed", "production", "completed"):
        raise HTTPException(
            status_code=400,
            detail="PO harus status confirmed (atau sudah produksi) sebelum production",
        )


@router.post("/production")
def create_production(
    body: ProductionCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "production", "ppic")),
) -> dict:
    if body.po_id is None:
        raise HTTPException(status_code=400, detail="po_id wajib")
    po = db.get(PoHeader, body.po_id)
    _require_po_confirmed(po)
    pdata = body.model_dump(exclude_unset=True)
    if not pdata.get("production_number"):
        pdata["production_number"] = next_number(db, "PRD", "PRD")
    row = ProductionOrder(**pdata)
    db.add(row)
    if po and po.status == "confirmed":
        po.status = "production"
    db.flush()
    log_change(
        db,
        entity_type="production",
        entity_id=row.id,
        action="create",
        after={"production_number": row.production_number, "po_id": row.po_id, "status": row.status},
        actor=user.username,
    )
    create_notification_for_roles(
        db,
        ("admin", "production", "ppic", "qc"),
        title=f"Production {row.production_number} dibuat",
        message=f"Referensi PO ID: {row.po_id}",
        category="production",
        entity_type="production",
        entity_id=row.id,
        route_path="/admin/production",
        route_query={"production_id": row.id},
    )
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.get("/production")
def list_production(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Search production no/po id"),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    _user=Depends(get_current_user),
) -> list[dict]:
    stmt = select(ProductionOrder).order_by(ProductionOrder.id.desc()).limit(limit).offset(offset)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(ProductionOrder.production_number.ilike(like))
    rows = db.scalars(stmt).all()
    return [row_to_dict(r) for r in rows]


@router.get("/production/{production_id}")
def get_production(
    production_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> dict:
    row = db.get(ProductionOrder, production_id)
    if not row:
        raise HTTPException(status_code=404, detail="Production tidak ditemukan")
    return row_to_dict(row)


@router.get("/production/{production_id}/details")
def list_production_details(
    production_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> list[dict]:
    if not db.get(ProductionOrder, production_id):
        raise HTTPException(status_code=404, detail="Production tidak ditemukan")
    rows = db.scalars(
        select(ProductionDetail)
        .where(ProductionDetail.production_id == production_id)
        .order_by(ProductionDetail.id.asc())
    ).all()
    return [row_to_dict(r) for r in rows]


@router.post("/production/{production_id}/details")
def add_production_detail(
    production_id: int,
    body: ProductionDetailCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "production")),
) -> dict:
    pr = db.get(ProductionOrder, production_id)
    if not pr:
        raise HTTPException(status_code=404, detail="Production tidak ditemukan")
    data = body.model_dump(exclude_unset=True)
    if data.get("po_detail_id") and not str(data.get("lot_number") or "").strip():
        pod = db.get(PoDetail, int(data["po_detail_id"]))
        if pod and (pod.thi_line_ref or "").strip():
            data["lot_number"] = pod.thi_line_ref.strip()
    row = ProductionDetail(
        production_id=production_id, **data
    )
    db.add(row)
    db.flush()
    log_change(
        db,
        entity_type="production_line",
        entity_id=row.id,
        action="create",
        after={"production_id": production_id, "po_detail_id": row.po_detail_id, "lot_number": row.lot_number},
        actor=user.username,
    )
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.put("/production-detail/{detail_id}")
def update_production_detail(
    detail_id: int,
    body: ProductionDetailUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "production")),
) -> dict:
    row = db.get(ProductionDetail, detail_id)
    if not row:
        raise HTTPException(status_code=404, detail="Detail production tidak ditemukan")
    before = {"qty_planned": row.qty_planned, "qty_actual": row.qty_actual, "status": row.status, "lot_number": row.lot_number}
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    log_change(
        db,
        entity_type="production_line",
        entity_id=row.id,
        action="update",
        before=before,
        after={"qty_planned": row.qty_planned, "qty_actual": row.qty_actual, "status": row.status, "lot_number": row.lot_number},
        actor=user.username,
    )
    db.commit()
    db.refresh(row)
    return row_to_dict(row)
