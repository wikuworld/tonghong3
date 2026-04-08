"""Sales Order (CR): alias domain untuk `po_headers` — nomor = SO-YYYYMM-xxxxx (field DB tetap po_number)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import PoDetail, PoHeader
from app.schemas import (
    PoDetailCreate,
    PoDetailOut,
    PoDetailUpdate,
    PoHeaderCreate,
    PoHeaderOut,
    PoHeaderUpdate,
)

router = APIRouter(tags=["sales-orders"])


@router.get("/sales-orders", response_model=list[PoHeaderOut])
def list_sales_orders(db: Session = Depends(get_db)) -> list[PoHeader]:
    return list(db.scalars(select(PoHeader).order_by(PoHeader.id.desc())).all())


@router.post("/sales-orders", response_model=PoHeaderOut)
def create_sales_order(body: PoHeaderCreate, db: Session = Depends(get_db)) -> PoHeader:
    from app.routers.po import create_po

    return create_po(body, db)


@router.get("/sales-orders/{so_id}", response_model=PoHeaderOut)
def get_sales_order(so_id: int, db: Session = Depends(get_db)) -> PoHeader:
    row = db.get(PoHeader, so_id)
    if not row:
        raise HTTPException(status_code=404, detail="Sales Order tidak ditemukan")
    return row


@router.put("/sales-orders/{so_id}", response_model=PoHeaderOut)
def update_sales_order(
    so_id: int, body: PoHeaderUpdate, db: Session = Depends(get_db)
) -> PoHeader:
    from app.routers.po import update_po

    return update_po(so_id, body, db)


@router.delete("/sales-orders/{so_id}")
def delete_sales_order(so_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    from app.routers.po import delete_po

    return delete_po(so_id, db)


@router.post("/sales-orders/{so_id}/details", response_model=PoDetailOut)
def add_so_detail(
    so_id: int, body: PoDetailCreate, db: Session = Depends(get_db)
) -> PoDetail:
    from app.routers.po import add_po_detail

    return add_po_detail(so_id, body, db)


@router.put("/sales-order-details/{detail_id}", response_model=PoDetailOut)
def update_so_detail(
    detail_id: int, body: PoDetailUpdate, db: Session = Depends(get_db)
) -> PoDetail:
    from app.routers.po import update_po_detail

    return update_po_detail(detail_id, body, db)


@router.delete("/sales-order-details/{detail_id}")
def delete_so_detail(detail_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    from app.routers.po import delete_po_detail

    return delete_po_detail(detail_id, db)
