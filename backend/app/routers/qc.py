from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
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

router = APIRouter(tags=["qc"])


def _eval_thickness_ok(
    actual: Decimal | None, tmin: Decimal | None, tmax: Decimal | None
) -> bool | None:
    if actual is None or tmin is None or tmax is None:
        return None
    return tmin <= actual <= tmax


@router.post("/qc")
def create_qc_header(body: QcHeaderCreate, db: Session = Depends(get_db)) -> dict:
    if body.production_id:
        pr = db.get(ProductionOrder, body.production_id)
        if not pr:
            raise HTTPException(status_code=404, detail="Production tidak ditemukan")
    row = QcHeader(**body.model_dump(exclude_unset=True))
    db.add(row)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.get("/qc")
def list_qc(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.scalars(select(QcHeader).order_by(QcHeader.id.desc())).all()
    return [row_to_dict(r) for r in rows]


@router.get("/qc/{qc_id}")
def get_qc(qc_id: int, db: Session = Depends(get_db)) -> dict:
    row = db.get(QcHeader, qc_id)
    if not row:
        raise HTTPException(status_code=404, detail="QC tidak ditemukan")
    return row_to_dict(row)


@router.get("/qc/{qc_id}/details")
def list_qc_details(qc_id: int, db: Session = Depends(get_db)) -> list[dict]:
    if not db.get(QcHeader, qc_id):
        raise HTTPException(status_code=404, detail="QC tidak ditemukan")
    rows = db.scalars(
        select(QcDetail).where(QcDetail.qc_id == qc_id).order_by(QcDetail.id.asc())
    ).all()
    return [row_to_dict(r) for r in rows]


@router.post("/qc/{qc_id}/details")
def add_qc_detail(qc_id: int, body: QcDetailCreate, db: Session = Depends(get_db)) -> dict:
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
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.put("/qc-detail/{detail_id}")
def update_qc_detail(
    detail_id: int, body: QcDetailUpdate, db: Session = Depends(get_db)
) -> dict:
    row = db.get(QcDetail, detail_id)
    if not row:
        raise HTTPException(status_code=404, detail="Detail QC tidak ditemukan")
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
    db.commit()
    db.refresh(row)
    return row_to_dict(row)
