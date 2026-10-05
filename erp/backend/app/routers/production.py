from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import PoDetail, PoHeader, ProductionDetail, ProductionOrder
from app.paging import apply_sort, page_dict, parse_page_params
from app.services.numbering import next_number
from app.schemas import (
    ProductionCreate,
    ProductionDetailCreate,
    ProductionDetailOut,
    ProductionDetailUpdate,
    ProductionOrderOut,
    ProductionOrderPageOut,
)
from app.routers.auth import get_current_user, require_roles
from app.services.audit import log_change
from app.services.notifications import create_notification_for_roles
from app.services.erp_book import reject_erp_shopfloor_write

router = APIRouter(tags=["production"])


def _require_po_confirmed(po: PoHeader | None) -> None:
    if not po:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")
    if po.status not in ("confirmed", "production", "completed"):
        raise HTTPException(
            status_code=400,
            detail="PO harus status confirmed (atau sudah produksi) sebelum production",
        )


@router.post("/production", response_model=ProductionOrderOut)
def create_production(
    body: ProductionCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "production", "ppic")),
) -> ProductionOrderOut:
    reject_erp_shopfloor_write()
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
    return row


@router.get("/production", response_model=ProductionOrderPageOut)
def list_production(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Search production no/po id"),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=200),
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    sort_by: Optional[str] = Query(None, description="date|code|status|start_date|created_at|production_number"),
    sort_dir: Optional[str] = Query(None),
    _user=Depends(get_current_user),
) -> dict:
    params = parse_page_params(
        page=page,
        page_size=page_size,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    stmt = select(ProductionOrder)
    count_stmt = select(func.count(ProductionOrder.id))
    if q:
        like = f"%{q}%"
        stmt = stmt.where(ProductionOrder.production_number.ilike(like))
        count_stmt = count_stmt.where(ProductionOrder.production_number.ilike(like))
    if status and str(status).strip():
        st = str(status).strip().lower()
        stmt = stmt.where(ProductionOrder.status == st)
        count_stmt = count_stmt.where(ProductionOrder.status == st)
    total = int(db.scalar(count_stmt) or 0)
    stmt = apply_sort(
        stmt,
        sortable={
            "date": ProductionOrder.start_date,
            "start_date": ProductionOrder.start_date,
            "created_at": ProductionOrder.created_at,
            "code": ProductionOrder.production_number,
            "production_number": ProductionOrder.production_number,
            "status": ProductionOrder.status,
            "id": ProductionOrder.id,
        },
        sort_by=params.sort_by,
        sort_dir=params.sort_dir,
        default_order=(ProductionOrder.id.desc(),),
    )
    items = list(db.scalars(stmt.limit(params.limit).offset(params.offset)).all())
    return page_dict(items=items, total=total, params=params)


@router.get("/production/{production_id}", response_model=ProductionOrderOut)
def get_production(
    production_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> ProductionOrderOut:
    row = db.get(ProductionOrder, production_id)
    if not row:
        raise HTTPException(status_code=404, detail="Production tidak ditemukan")
    return row


@router.get("/production/{production_id}/details", response_model=list[ProductionDetailOut])
def list_production_details(
    production_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> list[ProductionDetailOut]:
    if not db.get(ProductionOrder, production_id):
        raise HTTPException(status_code=404, detail="Production tidak ditemukan")
    rows = db.scalars(
        select(ProductionDetail)
        .where(ProductionDetail.production_id == production_id)
        .order_by(ProductionDetail.id.asc())
    ).all()
    return list(rows)


@router.post("/production/{production_id}/details", response_model=ProductionDetailOut)
def add_production_detail(
    production_id: int,
    body: ProductionDetailCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "production")),
) -> ProductionDetailOut:
    reject_erp_shopfloor_write()
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
    return row


@router.put("/production-detail/{detail_id}", response_model=ProductionDetailOut)
def update_production_detail(
    detail_id: int,
    body: ProductionDetailUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "production")),
) -> ProductionDetailOut:
    reject_erp_shopfloor_write()
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
    return row
