"""Query builder bersama untuk daftar header PO (GET /po & GET /po/page)."""

from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from app.models import PoDetail, PoHeader


def parse_query_date(s: Optional[str]) -> Optional[date]:
    if not s or not str(s).strip():
        return None
    try:
        return date.fromisoformat(str(s).strip()[:10])
    except ValueError:
        return None


def apply_po_list_filters(
    stmt: Select,
    *,
    mkt_workflow_stage: Optional[str] = None,
    q: Optional[str] = None,
    customer_id: Optional[int] = None,
    buyer: Optional[str] = None,
    status: Optional[str] = None,
    po_category: Optional[str] = None,
    order_date: Optional[str] = None,
    order_date_from: Optional[str] = None,
    order_date_to: Optional[str] = None,
) -> Select:
    if mkt_workflow_stage:
        stmt = stmt.where(PoHeader.mkt_workflow_stage == mkt_workflow_stage)
    if customer_id is not None:
        stmt = stmt.where(PoHeader.customer_id == customer_id)
    if buyer:
        stmt = stmt.where(PoHeader.buyer == buyer)
    if status:
        stmt = stmt.where(PoHeader.status == status)
    if po_category:
        stmt = stmt.where(PoHeader.po_category == po_category)
    d_from = parse_query_date(order_date_from)
    d_to = parse_query_date(order_date_to)
    d_one = parse_query_date(order_date)
    if d_from is not None or d_to is not None:
        if d_from is not None:
            stmt = stmt.where(PoHeader.order_date.is_not(None), PoHeader.order_date >= d_from)
        if d_to is not None:
            stmt = stmt.where(PoHeader.order_date.is_not(None), PoHeader.order_date <= d_to)
    elif d_one is not None:
        stmt = stmt.where(PoHeader.order_date == d_one)
    if q:
        like = f"%{q}%"
        po_ids_by_detail_material = select(PoDetail.po_id).where(PoDetail.material_name.ilike(like))
        stmt = stmt.where(
            or_(
                PoHeader.po_number.ilike(like),
                PoHeader.buyer.ilike(like),
                PoHeader.po_customer_ref.ilike(like),
                PoHeader.customer_name_snapshot.ilike(like),
                PoHeader.customer_code.ilike(like),
                PoHeader.id.in_(po_ids_by_detail_material),
            )
        )
    return stmt


def po_list_select(
    *,
    mkt_workflow_stage: Optional[str] = None,
    q: Optional[str] = None,
    customer_id: Optional[int] = None,
    buyer: Optional[str] = None,
    status: Optional[str] = None,
    po_category: Optional[str] = None,
    order_date: Optional[str] = None,
    order_date_from: Optional[str] = None,
    order_date_to: Optional[str] = None,
) -> Select:
    stmt = select(PoHeader)
    return apply_po_list_filters(
        stmt,
        mkt_workflow_stage=mkt_workflow_stage,
        q=q,
        customer_id=customer_id,
        buyer=buyer,
        status=status,
        po_category=po_category,
        order_date=order_date,
        order_date_from=order_date_from,
        order_date_to=order_date_to,
    )


def po_list_count(
    db: Session,
    *,
    mkt_workflow_stage: Optional[str] = None,
    q: Optional[str] = None,
    customer_id: Optional[int] = None,
    buyer: Optional[str] = None,
    status: Optional[str] = None,
    po_category: Optional[str] = None,
    order_date: Optional[str] = None,
    order_date_from: Optional[str] = None,
    order_date_to: Optional[str] = None,
) -> int:
    stmt = apply_po_list_filters(
        select(func.count(PoHeader.id)),
        mkt_workflow_stage=mkt_workflow_stage,
        q=q,
        customer_id=customer_id,
        buyer=buyer,
        status=status,
        po_category=po_category,
        order_date=order_date,
        order_date_from=order_date_from,
        order_date_to=order_date_to,
    )
    return int(db.scalar(stmt) or 0)
