"""Export CSV (CR §3.10)."""

from __future__ import annotations

import csv
import io
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models import PoDetail, PoHeader

router = APIRouter(tags=["reports"])


def _thickness_display(d: PoDetail | None) -> str:
    if not d:
        return "—"
    if d.thickness_text and str(d.thickness_text).strip():
        return str(d.thickness_text).strip()
    a, b = d.thickness_min, d.thickness_max
    if a is not None and b is not None:
        return f"{a} - {b}"
    if a is not None or b is not None:
        return str(a if a is not None else b)
    return "—"


def _qty_float(q: Decimal | None) -> float:
    if q is None:
        return 0.0
    return float(q)


def _header_matches_filters(
    h: PoHeader,
    date_from: Optional[date],
    date_to: Optional[date],
    customer: Optional[str],
) -> bool:
    if date_from is not None:
        if h.order_date is None or h.order_date < date_from:
            return False
    if date_to is not None:
        if h.order_date is None or h.order_date > date_to:
            return False
    if customer and str(customer).strip():
        q = str(customer).strip().lower()
        snap = (h.customer_name_snapshot or "").lower()
        code = (h.customer_code or "").lower()
        if not (q == snap or q == code or q in snap or q in code):
            return False
    return True


@router.get("/reports/po-order-description")
def report_po_order_description(
    db: Session = Depends(get_db),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    customer: Optional[str] = Query(None, description="Nama / kode customer (snapshot)"),
) -> dict[str, Any]:
    """Data untuk layar Reports: revisi ketebalan, order produksi, sample — dari PO aktual."""
    headers = db.scalars(
        select(PoHeader)
        .options(selectinload(PoHeader.details))
        .order_by(PoHeader.id.desc())
    ).all()

    revise: list[dict[str, Any]] = []
    production_orders: list[dict[str, Any]] = []
    samples: list[dict[str, Any]] = []

    for h in headers:
        if not _header_matches_filters(h, date_from, date_to, customer):
            continue
        cust = (h.customer_name_snapshot or h.customer_code or "").strip() or "—"
        po_no = h.po_number or f"SO-{h.id}"
        for ln in h.details or []:
            if ln.copied_from_detail_id:
                old = db.get(PoDetail, ln.copied_from_detail_id)
                revise.append(
                    {
                        "poNo": po_no,
                        "customer": cust,
                        "material": (ln.material_name or "").strip() or "—",
                        "oldThickness": _thickness_display(old),
                        "newThickness": _thickness_display(ln),
                        "qty": _qty_float(ln.quantity_order),
                    }
                )
            cat = (h.po_category or "production").lower()
            row = {
                "poNo": po_no,
                "customer": cust,
                "material": (ln.material_name or "").strip() or "—",
                "color": (ln.color or "").strip() or "—",
                "qty": _qty_float(ln.quantity_order),
                "status": h.status or "draft",
            }
            if cat == "sample":
                samples.append(row)
            else:
                production_orders.append(row)

    return {
        "revise_thickness": revise,
        "production_orders": production_orders,
        "samples": samples,
    }


@router.get("/reports/po-daily-recap.csv")
def export_po_daily_recap_csv(
    report_date: Optional[date] = Query(None, alias="date"),
    db: Session = Depends(get_db),
) -> Response:
    """Rekap laporan PO hari ini (filter tanggal order atau tanggal input = hari tersebut)."""
    d = report_date or date.today()
    headers = db.scalars(
        select(PoHeader)
        .where(
            or_(
                PoHeader.order_date == d,
                func.date(PoHeader.created_at) == d,
            )
        )
        .order_by(PoHeader.id.desc())
    ).all()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(
        [
            "so_number",
            "customer_id",
            "mkt_workflow_stage",
            "status",
            "order_date",
            "etd",
            "buyer",
            "rekap_printed_at",
        ]
    )
    for h in headers:
        w.writerow(
            [
                h.po_number or "",
                h.customer_id or "",
                h.mkt_workflow_stage or "",
                h.status or "",
                h.order_date or "",
                h.etd or "",
                h.buyer or "",
                h.rekap_printed_at.isoformat() if h.rekap_printed_at else "",
            ]
        )
    fn = f"rekap_po_{d.isoformat()}_{datetime.utcnow().strftime('%H%M')}.csv"
    return Response(
        content=buf.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{fn}"'},
    )


def _delivery_flat_columns(ln: PoDetail) -> list:
    """12 × (qty, date) selaras `03_Master_Data_Marketing.csv`."""
    by_seq = {d.sequence_no: d for d in (ln.delivery_schedules or [])}
    out = []
    for s in range(1, 13):
        d = by_seq.get(s)
        out.append(d.qty if d and d.qty is not None else "")
        out.append(d.delivery_date.isoformat() if d and d.delivery_date else "")
    return out


@router.get("/reports/sales-orders-export.csv")
def export_sales_orders_csv(db: Session = Depends(get_db)) -> Response:
    headers = db.scalars(select(PoHeader).order_by(PoHeader.id.desc())).all()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(
        [
            "so_number",
            "customer_id",
            "status",
            "order_date",
            "etd",
            "remark",
            "billing_address",
            "delivery_address",
            "marketing_excel_date_serial",
            "po_customer_ref",
            "order_type_label",
            "brand_name_snapshot",
            "customer_name_snapshot",
        ]
    )
    for h in headers:
        w.writerow(
            [
                h.po_number or "",
                h.customer_id or "",
                h.status or "",
                h.order_date or "",
                h.etd or "",
                (h.remark or "").replace("\n", " ")[:500],
                (h.billing_address or "").replace("\n", " ")[:300],
                (h.delivery_address or "").replace("\n", " ")[:300],
                h.marketing_excel_date_serial or "",
                (h.po_customer_ref or "").replace("\n", " ")[:500],
                h.order_type_label or "",
                h.brand_name_snapshot or "",
                h.customer_name_snapshot or "",
            ]
        )
    return Response(
        content=buf.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="sales_orders.csv"',
        },
    )


@router.get("/reports/sales-order-lines-export.csv")
def export_so_lines_csv(db: Session = Depends(get_db)) -> Response:
    lines = db.scalars(
        select(PoDetail)
        .options(selectinload(PoDetail.delivery_schedules))
        .order_by(PoDetail.id.desc())
    ).all()
    buf = io.StringIO()
    w = csv.writer(buf)
    base_cols = [
        "so_id",
        "line_id",
        "master_item_id",
        "copied_from_detail_id",
        "thi_line_ref",
        "material",
        "thickness_min",
        "thickness_max",
        "thickness_text",
        "emboss",
        "vir_softness_type",
        "color",
        "softness",
        "qty",
        "line_etd",
        "etd_excel_serial",
        "unit_price",
        "color_reference",
        "backing",
        "model",
        "style_article",
        "rtd_text",
        "stock_wh_qty",
        "balance_qty",
        "system_reference",
        "detail_remark",
    ]
    del_cols = []
    for i in range(1, 13):
        del_cols.extend([f"delivery_{i}_qty", f"delivery_{i}_date"])
    w.writerow(base_cols + del_cols)
    for ln in lines:
        w.writerow(
            [
                ln.po_id or "",
                ln.id,
                ln.master_item_id or "",
                ln.copied_from_detail_id or "",
                ln.thi_line_ref or "",
                ln.material_name or "",
                ln.thickness_min or "",
                ln.thickness_max or "",
                ln.thickness_text or "",
                ln.emboss or "",
                ln.vir_softness_type or "",
                ln.color or "",
                ln.softness or "",
                ln.quantity_order or "",
                ln.line_etd or "",
                ln.etd_excel_serial or "",
                ln.unit_price or "",
                ln.color_reference or "",
                ln.backing or "",
                ln.model or "",
                ln.style_article or "",
                ln.rtd_text or "",
                ln.stock_wh_qty or "",
                ln.balance_qty or "",
                ln.system_reference or "",
                (ln.detail_remark or "").replace("\n", " ")[:500],
            ]
            + _delivery_flat_columns(ln)
        )
    return Response(
        content=buf.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="sales_order_lines.csv"',
        },
    )
