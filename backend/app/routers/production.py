from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import PoHeader, ProductionDetail, ProductionOrder
from app.services.numbering import next_number
from app.schemas import (
    ProductionCreate,
    ProductionDetailCreate,
    ProductionDetailUpdate,
    row_to_dict,
)

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
def create_production(body: ProductionCreate, db: Session = Depends(get_db)) -> dict:
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
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.get("/production")
def list_production(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.scalars(select(ProductionOrder).order_by(ProductionOrder.id.desc())).all()
    return [row_to_dict(r) for r in rows]


@router.get("/production/{production_id}")
def get_production(production_id: int, db: Session = Depends(get_db)) -> dict:
    row = db.get(ProductionOrder, production_id)
    if not row:
        raise HTTPException(status_code=404, detail="Production tidak ditemukan")
    return row_to_dict(row)


@router.get("/production/{production_id}/details")
def list_production_details(production_id: int, db: Session = Depends(get_db)) -> list[dict]:
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
    production_id: int, body: ProductionDetailCreate, db: Session = Depends(get_db)
) -> dict:
    pr = db.get(ProductionOrder, production_id)
    if not pr:
        raise HTTPException(status_code=404, detail="Production tidak ditemukan")
    row = ProductionDetail(
        production_id=production_id, **body.model_dump(exclude_unset=True)
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.put("/production-detail/{detail_id}")
def update_production_detail(
    detail_id: int, body: ProductionDetailUpdate, db: Session = Depends(get_db)
) -> dict:
    row = db.get(ProductionDetail, detail_id)
    if not row:
        raise HTTPException(status_code=404, detail="Detail production tidak ditemukan")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)
