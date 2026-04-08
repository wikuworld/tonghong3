from __future__ import annotations

from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import (
    ProductionDetail,
    ProductionOrder,
    QcDetail,
    QcHeader,
)
from app.schemas import QcDetailCreate, QcDetailUpdate, QcHeaderCreate, row_to_dict
from app.routers.auth import get_current_user, require_roles
from app.services.audit import log_change
from app.services.notifications import create_notification_for_roles

router = APIRouter(tags=["qc"])


def _eval_thickness_ok(
    actual: Decimal | None, tmin: Decimal | None, tmax: Decimal | None
) -> bool | None:
    if actual is None or tmin is None or tmax is None:
        return None
    return tmin <= actual <= tmax


@router.post("/qc")
def create_qc_header(
    body: QcHeaderCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "qc")),
) -> dict:
    if body.production_id:
        pr = db.get(ProductionOrder, body.production_id)
        if not pr:
            raise HTTPException(status_code=404, detail="Production tidak ditemukan")
    row = QcHeader(**body.model_dump(exclude_unset=True))
    db.add(row)
    db.flush()
    log_change(
        db,
        entity_type="qc",
        entity_id=row.id,
        action="create",
        after={"qc_number": row.qc_number, "production_id": row.production_id, "qc_date": row.qc_date},
        actor=user.username,
    )
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.get("/qc")
def list_qc(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Search qc number"),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    _user=Depends(get_current_user),
) -> list[dict]:
    stmt = select(QcHeader).order_by(QcHeader.id.desc()).limit(limit).offset(offset)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(QcHeader.qc_number.ilike(like))
    rows = db.scalars(stmt).all()
    return [row_to_dict(r) for r in rows]


@router.get("/qc/{qc_id}")
def get_qc(qc_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)) -> dict:
    row = db.get(QcHeader, qc_id)
    if not row:
        raise HTTPException(status_code=404, detail="QC tidak ditemukan")
    return row_to_dict(row)


@router.get("/qc/{qc_id}/details")
def list_qc_details(
    qc_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> list[dict]:
    if not db.get(QcHeader, qc_id):
        raise HTTPException(status_code=404, detail="QC tidak ditemukan")
    rows = db.scalars(
        select(QcDetail).where(QcDetail.qc_id == qc_id).order_by(QcDetail.id.asc())
    ).all()
    return [row_to_dict(r) for r in rows]


@router.post("/qc/{qc_id}/details")
def add_qc_detail(
    qc_id: int,
    body: QcDetailCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "qc")),
) -> dict:
    hdr = db.get(QcHeader, qc_id)
    if not hdr:
        raise HTTPException(status_code=404, detail="QC header tidak ditemukan")
    if body.production_detail_id:
        pd = db.get(ProductionDetail, body.production_detail_id)
        if not pd:
            raise HTTPException(status_code=404, detail="Production detail tidak ada")

    data = body.model_dump(exclude_unset=True)
    thickness_ok = _eval_thickness_ok(
        body.thickness_actual, body.thickness_min, body.thickness_max
    )
    if thickness_ok is not None:
        data["is_ok"] = thickness_ok
        data["result"] = "ok" if thickness_ok else "ng"
    elif body.is_ok is not None:
        data["result"] = "ok" if body.is_ok else "ng"

    row = QcDetail(qc_id=qc_id, **{k: v for k, v in data.items() if k != "qc_id"})
    db.add(row)
    db.flush()
    log_change(
        db,
        entity_type="qc_line",
        entity_id=row.id,
        action="create",
        after={"qc_id": qc_id, "production_detail_id": row.production_detail_id, "result": row.result, "is_ok": row.is_ok},
        actor=user.username,
    )
    if row.is_ok is False:
        create_notification_for_roles(
            db,
            ("admin", "qc", "production", "ppic"),
            title=f"QC NG pada detail {row.id}",
            message=f"QC {qc_id} menghasilkan status NG",
            category="qc",
            entity_type="qc_line",
            entity_id=row.id,
            route_path="/admin/qc",
            route_query={"qc_id": qc_id, "qc_detail_id": row.id},
        )
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.put("/qc-detail/{detail_id}")
def update_qc_detail(
    detail_id: int,
    body: QcDetailUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "qc")),
) -> dict:
    row = db.get(QcDetail, detail_id)
    if not row:
        raise HTTPException(status_code=404, detail="Detail QC tidak ditemukan")
    before = {"thickness_actual": row.thickness_actual, "result": row.result, "is_ok": row.is_ok, "remark": row.remark}
    data = body.model_dump(exclude_unset=True)
    thickness_ok = _eval_thickness_ok(
        data.get("thickness_actual", row.thickness_actual),
        data.get("thickness_min", row.thickness_min),
        data.get("thickness_max", row.thickness_max),
    )
    if thickness_ok is not None:
        data["is_ok"] = thickness_ok
        data["result"] = "ok" if thickness_ok else "ng"
    for k, v in data.items():
        setattr(row, k, v)
    log_change(
        db,
        entity_type="qc_line",
        entity_id=row.id,
        action="update",
        before=before,
        after={"thickness_actual": row.thickness_actual, "result": row.result, "is_ok": row.is_ok, "remark": row.remark},
        actor=user.username,
    )
    db.commit()
    db.refresh(row)
    return row_to_dict(row)
