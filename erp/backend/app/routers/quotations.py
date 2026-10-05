"""Penawaran (quotation) — inquiry, header, baris material."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, noload, selectinload

from app.db import get_db
from app.models import Customer, MasterItem, QuotationHeader, QuotationLine
from app.paging import apply_sort, page_dict, parse_page_params
from app.routers.auth import get_current_user, require_roles
from app.schemas import (
    QuotationHeaderCreate,
    QuotationHeaderOut,
    QuotationHeaderUpdate,
    QuotationLineCreate,
    QuotationLineOut,
    QuotationLineUpdate,
)
from app.services.numbering import next_number

router = APIRouter(tags=["quotations"])


def _dec(v: Decimal | None) -> Decimal:
    return v if v is not None else Decimal(0)


def _compute_line_amount(
    qty: Decimal | None,
    unit_price: Decimal | None,
    discount_amount: Decimal | None,
    tax_rate_pct: Decimal | None,
) -> Decimal:
    base = _dec(qty) * _dec(unit_price) - _dec(discount_amount)
    if base < 0:
        base = Decimal(0)
    tr = _dec(tax_rate_pct)
    amt = base * (Decimal(1) + tr / Decimal(100))
    return amt.quantize(Decimal("0.01"))


def _recalc_header_total(db: Session, header_id: int) -> None:
    hdr = db.get(QuotationHeader, header_id)
    if not hdr:
        return
    lines = db.scalars(
        select(QuotationLine).where(QuotationLine.quotation_id == header_id).order_by(QuotationLine.line_no.asc())
    ).all()
    total = sum((_dec(l.line_amount) for l in lines), Decimal(0))
    hdr.total_amount = total.quantize(Decimal("0.01"))
    hdr.updated_at = datetime.utcnow()


def _serialize_header(h: QuotationHeader, db: Session, include_lines: bool) -> QuotationHeaderOut:
    cust_name = None
    if h.customer_id:
        c = db.get(Customer, h.customer_id)
        if c and (c.name or "").strip():
            cust_name = (c.name or "").strip()
    final_lines: list[QuotationLineOut] = []
    if include_lines:
        final_lines = [QuotationLineOut.model_validate(x) for x in (h.lines or [])]
    base = QuotationHeaderOut.model_validate(h)
    return base.model_copy(update={"customer_name": cust_name, "lines": final_lines})


@router.get("/quotations")
def list_quotations(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Nomor penawaran / remark"),
    customer_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=200),
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    sort_by: Optional[str] = Query(None, description="date|code|status|quotation_date|quotation_number"),
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
    stmt = select(QuotationHeader).options(noload(QuotationHeader.lines))
    count_stmt = select(func.count(QuotationHeader.id))
    if customer_id is not None:
        stmt = stmt.where(QuotationHeader.customer_id == customer_id)
        count_stmt = count_stmt.where(QuotationHeader.customer_id == customer_id)
    if status and str(status).strip():
        s = str(status).strip().lower()
        stmt = stmt.where(QuotationHeader.status == s)
        count_stmt = count_stmt.where(QuotationHeader.status == s)
    if date_from is not None:
        clause = or_(QuotationHeader.quotation_date.is_(None), QuotationHeader.quotation_date >= date_from)
        stmt = stmt.where(clause)
        count_stmt = count_stmt.where(clause)
    if date_to is not None:
        clause = or_(QuotationHeader.quotation_date.is_(None), QuotationHeader.quotation_date <= date_to)
        stmt = stmt.where(clause)
        count_stmt = count_stmt.where(clause)
    if q and str(q).strip():
        like = f"%{str(q).strip()}%"
        where_q = or_(
            QuotationHeader.quotation_number.ilike(like),
            QuotationHeader.remark.ilike(like),
            QuotationHeader.salesperson.ilike(like),
        )
        stmt = stmt.where(where_q)
        count_stmt = count_stmt.where(where_q)
    total = int(db.scalar(count_stmt) or 0)
    stmt = apply_sort(
        stmt,
        sortable={
            "date": QuotationHeader.quotation_date,
            "quotation_date": QuotationHeader.quotation_date,
            "code": QuotationHeader.quotation_number,
            "quotation_number": QuotationHeader.quotation_number,
            "status": QuotationHeader.status,
            "id": QuotationHeader.id,
        },
        sort_by=params.sort_by,
        sort_dir=params.sort_dir,
        default_order=(QuotationHeader.id.desc(),),
    )
    rows = list(db.scalars(stmt.limit(params.limit).offset(params.offset)).all())
    items = [_serialize_header(h, db, include_lines=False) for h in rows]
    return page_dict(items=items, total=total, params=params)


@router.get("/quotations/{quotation_id}", response_model=QuotationHeaderOut)
def get_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> QuotationHeaderOut:
    h = db.scalars(
        select(QuotationHeader)
        .options(selectinload(QuotationHeader.lines))
        .where(QuotationHeader.id == quotation_id)
    ).first()
    if not h:
        raise HTTPException(status_code=404, detail="Penawaran tidak ditemukan")
    return _serialize_header(h, db, include_lines=True)


@router.post("/quotations", response_model=QuotationHeaderOut)
def create_quotation(
    body: QuotationHeaderCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "marketing", "sales")),
) -> QuotationHeaderOut:
    data = body.model_dump(exclude_unset=True)
    data.setdefault("status", "draft")
    if not data.get("quotation_date"):
        data["quotation_date"] = date.today()
    num = next_number(db, "QUO", "Q")
    row = QuotationHeader(
        quotation_number=num,
        customer_id=data.get("customer_id"),
        quotation_date=data.get("quotation_date"),
        currency=data.get("currency") or "USD",
        payment_terms=data.get("payment_terms"),
        valid_until=data.get("valid_until"),
        salesperson=data.get("salesperson"),
        remark=data.get("remark"),
        status=data.get("status") or "draft",
    )
    db.add(row)
    db.flush()
    _recalc_header_total(db, row.id)
    db.commit()
    db.refresh(row)
    h = db.scalars(
        select(QuotationHeader)
        .options(selectinload(QuotationHeader.lines))
        .where(QuotationHeader.id == row.id)
    ).first()
    assert h is not None
    return _serialize_header(h, db, include_lines=True)


@router.put("/quotations/{quotation_id}", response_model=QuotationHeaderOut)
def update_quotation(
    quotation_id: int,
    body: QuotationHeaderUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "marketing", "sales")),
) -> QuotationHeaderOut:
    row = db.get(QuotationHeader, quotation_id)
    if not row:
        raise HTTPException(status_code=404, detail="Penawaran tidak ditemukan")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    row.updated_at = datetime.utcnow()
    db.commit()
    h = db.scalars(
        select(QuotationHeader)
        .options(selectinload(QuotationHeader.lines))
        .where(QuotationHeader.id == quotation_id)
    ).first()
    assert h is not None
    return _serialize_header(h, db, include_lines=True)


@router.delete("/quotations/{quotation_id}")
def delete_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "marketing")),
) -> dict[str, str]:
    row = db.get(QuotationHeader, quotation_id)
    if not row:
        raise HTTPException(status_code=404, detail="Penawaran tidak ditemukan")
    db.delete(row)
    db.commit()
    return {"status": "deleted"}


@router.post("/quotations/{quotation_id}/lines", response_model=QuotationLineOut)
def add_quotation_line(
    quotation_id: int,
    body: QuotationLineCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "marketing", "sales")),
) -> QuotationLineOut:
    hdr = db.get(QuotationHeader, quotation_id)
    if not hdr:
        raise HTTPException(status_code=404, detail="Penawaran tidak ditemukan")
    last = db.scalars(
        select(QuotationLine.line_no)
        .where(QuotationLine.quotation_id == quotation_id)
        .order_by(QuotationLine.line_no.desc())
        .limit(1)
    ).first()
    next_no = int(last or 0) + 1
    d = body.model_dump(exclude_unset=True)
    mi: MasterItem | None = None
    if d.get("master_item_id"):
        mi = db.get(MasterItem, int(d["master_item_id"]))
        if mi:
            d.setdefault("item_code", mi.item_code)
            if not d.get("description"):
                parts = [p for p in [mi.material_name, mi.thickness_range or str(mi.thickness_mm or "")] if p]
                d["description"] = " ".join(parts) if parts else mi.item_code
            d.setdefault("color", mi.color)
    qty = d.get("quantity")
    up = d.get("unit_price")
    disc = d.get("discount_amount")
    tr = d.get("tax_rate")
    line_amt = _compute_line_amount(qty, up, disc, tr)
    line = QuotationLine(
        quotation_id=quotation_id,
        line_no=next_no,
        item_code=d.get("item_code"),
        description=d.get("description"),
        color=d.get("color"),
        specification=d.get("specification"),
        quantity=qty,
        unit=d.get("unit") or "S/F",
        unit_price=up,
        discount_amount=disc if disc is not None else Decimal(0),
        tax_rate=tr if tr is not None else Decimal(0),
        line_amount=line_amt,
        master_item_id=d.get("master_item_id"),
    )
    db.add(line)
    db.flush()
    _recalc_header_total(db, quotation_id)
    db.commit()
    db.refresh(line)
    return QuotationLineOut.model_validate(line)


@router.put("/quotation-lines/{line_id}", response_model=QuotationLineOut)
def update_quotation_line(
    line_id: int,
    body: QuotationLineUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "marketing", "sales")),
) -> QuotationLineOut:
    row = db.get(QuotationLine, line_id)
    if not row:
        raise HTTPException(status_code=404, detail="Baris tidak ditemukan")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    row.line_amount = _compute_line_amount(
        row.quantity, row.unit_price, row.discount_amount, row.tax_rate
    )
    db.flush()
    _recalc_header_total(db, int(row.quotation_id or 0))
    db.commit()
    db.refresh(row)
    return QuotationLineOut.model_validate(row)


@router.delete("/quotation-lines/{line_id}")
def delete_quotation_line(
    line_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "marketing", "sales")),
) -> dict[str, str]:
    row = db.get(QuotationLine, line_id)
    if not row:
        raise HTTPException(status_code=404, detail="Baris tidak ditemukan")
    qid = int(row.quotation_id or 0)
    db.delete(row)
    db.flush()
    _recalc_header_total(db, qid)
    db.commit()
    return {"status": "deleted"}
