"""Endpoint format lembar marketing (outstanding) dari data PO aktual."""

from __future__ import annotations

import csv
import io
from decimal import Decimal
from enum import Enum
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models import (
    Customer,
    DeliveryDetail,
    DeliveryHeader,
    Invoice,
    PoDetail,
    PoHeader,
    ProductionDetail,
)

router = APIRouter(tags=["marketing"])


class BalanceFilter(str, Enum):
    """Filter baris berdasarkan saldo baris PO (kolom balance_qty)."""

    all = "all"
    exclude_zero = "exclude_zero"
    positive_only = "positive_only"


def _passes_balance_filter(ln: PoDetail, mode: BalanceFilter) -> bool:
    b = ln.balance_qty
    if mode == BalanceFilter.all:
        return True
    if mode == BalanceFilter.exclude_zero:
        if b is None:
            return True
        return b != 0
    if mode == BalanceFilter.positive_only:
        if b is None:
            return False
        return b > 0
    return True


def _dec_str(v: Decimal | None) -> str:
    if v is None:
        return ""
    return str(v)


def _thickness_display(ln: PoDetail) -> str:
    if ln.thickness_text and str(ln.thickness_text).strip():
        return str(ln.thickness_text).strip()
    a, b = ln.thickness_min, ln.thickness_max
    if a is not None and b is not None:
        return f"{a} - {b}"
    if a is not None or b is not None:
        return str(a if a is not None else b)
    return ""


def _order_type_marketing(h: PoHeader) -> str:
    if h.order_type_label and str(h.order_type_label).strip():
        return str(h.order_type_label).strip().upper()[:40]
    c = (h.po_category or "production").lower()
    alias = {
        "production": "PROD",
        "sample": "SAMPLE",
    }
    return alias.get(c, c.upper()[:20])


def _line_to_row(h: PoHeader, ln: PoDetail) -> dict[str, Any]:
    brand = (h.brand_name_snapshot or "").strip() or "—"
    cust = (h.customer_name_snapshot or h.customer_code or "").strip() or "—"
    thi = (ln.thi_line_ref or "").strip() or "—"
    return {
        "order_date": h.order_date.isoformat() if h.order_date else None,
        "thi_order": thi,
        "customer_name": cust,
        "brand": brand,
        "order_type": _order_type_marketing(h),
        "no_po": (h.po_number or "").strip() or "—",
        "material_name": (ln.material_name or "").strip() or "—",
        "thickness": _thickness_display(ln),
        "emboss": (ln.emboss or "").strip() or "",
        "softness_type": (ln.vir_softness_type or "").strip() or "",
        "color": (ln.color or "").strip() or "",
        "softness": (ln.softness or "").strip() or "",
        "qty_sf": _dec_str(ln.quantity_order),
        "unit_price": _dec_str(ln.unit_price),
        "color_reference": (ln.color_reference or "").strip() or "",
        "backing": (ln.backing or "").strip() or "",
        "model": (ln.model or "").strip() or "",
        "style_article": (ln.style_article or "").strip() or "",
        "rtd_text": (ln.rtd_text or "").strip() or "",
        "line_etd": ln.line_etd.isoformat() if ln.line_etd else None,
        "stock_wh_qty": _dec_str(ln.stock_wh_qty),
        "balance_qty": _dec_str(ln.balance_qty),
        "system_reference": (ln.system_reference or "").strip() or "",
        "detail_remark": (ln.detail_remark or "").strip() or "",
        "po_id": h.id,
        "po_detail_id": ln.id,
        "po_status": h.status or "",
        "mkt_stage": h.mkt_workflow_stage or "",
    }


def _query_outstanding_rows(
    db: Session, balance_filter: BalanceFilter = BalanceFilter.exclude_zero
) -> list[dict[str, Any]]:
    """Baris dari PO yang belum completed (aliran outstanding marketing)."""
    headers = db.scalars(
        select(PoHeader)
        .options(selectinload(PoHeader.details))
        .order_by(PoHeader.id.desc())
    ).all()
    out: list[dict[str, Any]] = []
    for h in headers:
        if (h.status or "").lower() == "completed":
            continue
        for ln in h.details or []:
            if not _passes_balance_filter(ln, balance_filter):
                continue
            out.append(_line_to_row(h, ln))
    return out


def _delivery_detail_to_row(
    dd: DeliveryDetail,
    dh: DeliveryHeader,
    pd: Optional[ProductionDetail],
    pod: Optional[PoDetail],
    ph: Optional[PoHeader],
    cust: Optional[Customer],
    inv: Optional[Invoice],
) -> dict[str, Any]:
    factory = ""
    if cust and (cust.name or "").strip():
        factory = (cust.name or "").strip()
    elif ph and (ph.customer_name_snapshot or ph.customer_code or "").strip():
        factory = (ph.customer_name_snapshot or ph.customer_code or "").strip()
    elif dh.destination:
        factory = (dh.destination or "")[:255]

    system_no = ""
    if pod:
        system_no = (pod.system_reference or pod.thi_line_ref or "").strip()

    lot_no = ""
    if pd and pd.lot_number:
        lot_no = (pd.lot_number or "").strip()

    return {
        "surat_jalan_no": (dh.delivery_number or "").strip() or "—",
        "delivery_date": dh.delivery_date.isoformat() if dh.delivery_date else None,
        "factory_name": factory or "—",
        "system_no": system_no or "—",
        "po_date": ph.order_date.isoformat() if ph and ph.order_date else None,
        "po_number": (ph.po_number or "").strip() if ph else "",
        "lot_no": lot_no,
        "thickness": _thickness_display(pod) if pod else "",
        "color": (pod.color or "").strip() if pod else "",
        "material_type": (pod.vir_softness_type or "").strip() if pod else "",
        "material_name": (pod.material_name or "").strip() if pod else "",
        "qty_po": _dec_str(pod.quantity_order) if pod else "",
        "unit_price": _dec_str(pod.unit_price) if pod else "",
        "qty_roll": dd.qty_roll if dd.qty_roll is not None else None,
        "qty_pcs": dd.qty_pcs if dd.qty_pcs is not None else None,
        "qty_sf": _dec_str(dd.qty),
        "weight": _dec_str(dd.weight),
        "color_std": (pod.color_reference or "").strip() if pod else "",
        "emboss": (pod.emboss or "").strip() if pod else "",
        "buyer": (ph.buyer or "").strip() if ph else "",
        "style_article": (pod.style_article or "").strip() if pod else "",
        "model": (pod.model or "").strip() if pod else "",
        "invoice_number": (inv.invoice_number or "").strip() if inv else "",
        "pi_no": (ph.po_customer_ref or "").strip() if ph else "",
        "remark": (ph.remark or "").strip() if ph and ph.remark else "",
        "destination": (dh.destination or "").strip() if dh.destination else "",
        "delivery_id": dh.id,
        "delivery_detail_id": dd.id,
        "delivery_status": dh.status or "",
    }


def _query_delivery_lines_rows(db: Session) -> list[dict[str, Any]]:
    """Baris delivery + join ke produksi & PO (format lembar DELIVERY LIST)."""
    stmt = (
        select(DeliveryDetail, DeliveryHeader, ProductionDetail, PoDetail, PoHeader, Customer)
        .join(DeliveryHeader, DeliveryDetail.delivery_id == DeliveryHeader.id)
        .outerjoin(ProductionDetail, DeliveryDetail.production_detail_id == ProductionDetail.id)
        .outerjoin(PoDetail, ProductionDetail.po_detail_id == PoDetail.id)
        .outerjoin(PoHeader, PoDetail.po_id == PoHeader.id)
        .outerjoin(Customer, DeliveryHeader.customer_id == Customer.id)
        .order_by(DeliveryHeader.id.desc(), DeliveryDetail.id.asc())
    )
    raw = db.execute(stmt).all()
    if not raw:
        return []

    delivery_ids = {row[1].id for row in raw}
    inv_by_delivery: dict[int, Invoice] = {}
    if delivery_ids:
        inv_rows = db.scalars(
            select(Invoice).where(Invoice.delivery_id.in_(delivery_ids))
        ).all()
        for inv in inv_rows:
            did = inv.delivery_id
            if did is None:
                continue
            if did not in inv_by_delivery:
                inv_by_delivery[did] = inv

    out: list[dict[str, Any]] = []
    for dd, dh, pd, pod, ph, cust in raw:
        inv = inv_by_delivery.get(dh.id)
        out.append(_delivery_detail_to_row(dd, dh, pd, pod, ph, cust, inv))
    return out


@router.get("/marketing/outstanding-lines")
def marketing_outstanding_lines(
    db: Session = Depends(get_db),
    balance_filter: BalanceFilter = Query(
        default=BalanceFilter.exclude_zero,
        description="all: semua baris; exclude_zero: sembunyikan balance tepat 0; positive_only: hanya balance > 0",
    ),
) -> list[dict[str, Any]]:
    return _query_outstanding_rows(db, balance_filter)


@router.get("/marketing/outstanding-lines.csv")
def marketing_outstanding_lines_csv(
    db: Session = Depends(get_db),
    balance_filter: BalanceFilter = Query(default=BalanceFilter.exclude_zero),
) -> Response:
    rows = _query_outstanding_rows(db, balance_filter)
    buf = io.StringIO()
    if not rows:
        w = csv.writer(buf)
        w.writerow(["order_date", "thi_order", "customer_name", "no_po", "material_name"])
    else:
        fieldnames = list(rows[0].keys())
        w = csv.DictWriter(buf, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    return Response(
        content=buf.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="marketing_outstanding.csv"'},
    )


@router.get("/marketing/delivery-lines")
def marketing_delivery_lines(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    return _query_delivery_lines_rows(db)


@router.get("/marketing/delivery-lines.csv")
def marketing_delivery_lines_csv(db: Session = Depends(get_db)) -> Response:
    rows = _query_delivery_lines_rows(db)
    buf = io.StringIO()
    if not rows:
        w = csv.writer(buf)
        w.writerow(
            [
                "surat_jalan_no",
                "delivery_date",
                "factory_name",
                "system_no",
                "po_number",
            ]
        )
    else:
        fieldnames = list(rows[0].keys())
        w = csv.DictWriter(buf, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    return Response(
        content=buf.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="marketing_delivery_list.csv"'},
    )
