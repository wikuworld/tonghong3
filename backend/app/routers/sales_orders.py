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
from app.routers.auth import get_current_user, require_roles

router = APIRouter(tags=["sales-orders"])


@router.get("/sales-orders", response_model=list[PoHeaderOut])
def list_sales_orders(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> list[PoHeader]:
    return list(db.scalars(select(PoHeader).order_by(PoHeader.id.desc())).all())


@router.post("/sales-orders", response_model=PoHeaderOut)
def create_sales_order(
    body: PoHeaderCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "marketing", "sales")),
) -> PoHeader:
    from app.routers.po import create_po

    return create_po(body, db, user)


@router.get("/sales-orders/{so_id}", response_model=PoHeaderOut)
def get_sales_order(
    so_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> PoHeader:
    row = db.get(PoHeader, so_id)
    if not row:
        raise HTTPException(status_code=404, detail="Sales Order tidak ditemukan")
    return row


@router.put("/sales-orders/{so_id}", response_model=PoHeaderOut)
def update_sales_order(
    so_id: int,
    body: PoHeaderUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "marketing", "ppic")),
) -> PoHeader:
    from app.routers.po import update_po

    return update_po(so_id, body, db, user)


@router.delete("/sales-orders/{so_id}")
def delete_sales_order(
    so_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> dict[str, str]:
    from app.routers.po import delete_po

    return delete_po(so_id, db, user)


@router.post("/sales-orders/{so_id}/details", response_model=PoDetailOut)
def add_so_detail(
    so_id: int,
    body: PoDetailCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing", "sales")),
) -> PoDetail:
    from app.routers.po import add_po_detail

    return add_po_detail(so_id, body, db, user=_user)


@router.put("/sales-order-details/{detail_id}", response_model=PoDetailOut)
def update_so_detail(
    detail_id: int,
    body: PoDetailUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "marketing", "ppic", "finance")),
) -> PoDetail:
    from app.routers.po import update_po_detail

    return update_po_detail(detail_id, body, db, user)


@router.delete("/sales-order-details/{detail_id}")
def delete_so_detail(
    detail_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> dict[str, str]:
    from app.routers.po import delete_po_detail

    return delete_po_detail(detail_id, db, user)
