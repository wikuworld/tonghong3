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
from app.routers.auth import get_current_user

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


def _order_type_label(h: PoHeader) -> str:
    """Selaras lembar marketing / LAPORAN PO HARIAN."""
    if h.order_type_label and str(h.order_type_label).strip():
        return str(h.order_type_label).strip().upper()[:40]
    c = (h.po_category or "production").lower()
    alias = {
        "production": "PROD",
        "sample": "SAMPLE",
        "claim": "CLAIM",
        "return": "RETURN",
        "subcont": "SUBKON",
        "suede": "SUEDE",
    }
    return alias.get(c, c.upper()[:20])


def _pu_production_note(ln: PoDetail) -> str:
    vt = (ln.vir_softness_type or "").lower()
    if "vir" in vt or "pu" in vt:
        return "PU COATED (PU)"
    return ""


def _price_str(ln: PoDetail) -> str:
    if ln.unit_price is None:
        return ""
    return str(ln.unit_price)


def _header_matches_date_filters(
    h: PoHeader,
    date_from: Optional[date],
    date_to: Optional[date],
    date_field: str,
) -> bool:
    if date_from is None and date_to is None:
        return True

    def in_range(d: Optional[date]) -> bool:
        if d is None:
            return False
        if date_from is not None and d < date_from:
            return False
        if date_to is not None and d > date_to:
            return False
        return True

    order_ok = in_range(h.order_date)
    created_ok = False
    if h.created_at:
        ca = h.created_at
        cd: Optional[date] = ca.date() if isinstance(ca, datetime) else ca  # type: ignore[assignment]
        created_ok = in_range(cd)

    df = (date_field or "order").strip().lower()
    if df == "created":
        return created_ok
    if df == "either":
        return order_ok or created_ok
    return order_ok


def _header_matches_filters(
    h: PoHeader,
    date_from: Optional[date],
    date_to: Optional[date],
    customer: Optional[str],
    date_field: str = "order",
) -> bool:
    if not _header_matches_date_filters(h, date_from, date_to, date_field):
        return False
    if customer and str(customer).strip():
        q = str(customer).strip().lower()
        snap = (h.customer_name_snapshot or "").lower()
        code = (h.customer_code or "").lower()
        if not (q == snap or q == code or q in snap or q in code):
            return False
    return True


def _base_marketing_daily_row(h: PoHeader, ln: PoDetail) -> dict[str, Any]:
    cust = (h.customer_name_snapshot or h.customer_code or "").strip() or "—"
    po_no = h.po_number or f"SO-{h.id}"
    return {
        "poNo": po_no,
        "po_customer_ref": (h.po_customer_ref or "").strip(),
        "customer": cust,
        "brand": (h.brand_name_snapshot or "").strip(),
        "order_type": _order_type_label(h),
        "buyer": (h.buyer or "").strip(),
        "order_date": h.order_date.isoformat() if h.order_date else None,
        "thi_line_ref": (ln.thi_line_ref or "").strip(),
        "material": (ln.material_name or "").strip() or "—",
        "thickness": _thickness_display(ln),
        "emboss": (ln.emboss or "").strip(),
        "softness_type": (ln.vir_softness_type or "").strip(),
        "pu_production": _pu_production_note(ln),
        "color": (ln.color or "").strip(),
        "softness": (ln.softness or "").strip(),
        "unit_price": _price_str(ln),
        "color_reference": (ln.color_reference or "").strip(),
        "backing": (ln.backing or "").strip(),
        "model": (ln.model or "").strip(),
        "style_article": (ln.style_article or "").strip(),
        "line_etd": ln.line_etd.isoformat() if ln.line_etd else None,
        "qty": _qty_float(ln.quantity_order),
        "po_category": (h.po_category or "production").lower(),
        "status": h.status or "draft",
        "po_id": h.id,
        "detail_id": ln.id,
    }


def _build_marketing_daily_payload(
    db: Session,
    date_from: Optional[date],
    date_to: Optional[date],
    customer: Optional[str],
    date_field: str,
) -> dict[str, Any]:
    """Isi JSON + CSV laporan PO harian marketing."""
    headers = db.scalars(
        select(PoHeader)
        .options(selectinload(PoHeader.details))
        .order_by(PoHeader.id.desc())
    ).all()

    revise: list[dict[str, Any]] = []
    production_orders: list[dict[str, Any]] = []
    samples: list[dict[str, Any]] = []

    df = (date_field or "order").strip().lower()
    if df not in {"order", "created", "either"}:
        df = "order"

    for h in headers:
        if not _header_matches_filters(h, date_from, date_to, customer, df):
            continue
        for ln in h.details or []:
            if ln.copied_from_detail_id:
                old = db.get(PoDetail, ln.copied_from_detail_id)
                row = _base_marketing_daily_row(h, ln)
                row["oldThickness"] = _thickness_display(old)
                row["newThickness"] = _thickness_display(ln)
                revise.append(row)
                continue

            cat = (h.po_category or "production").lower()
            row = _base_marketing_daily_row(h, ln)
            row["oldThickness"] = ""
            row["newThickness"] = ""
            if cat == "sample":
                samples.append(row)
            else:
                production_orders.append(row)

    return {
        "report_title": "LAPORAN PO HARIAN MARKETING",
        "revise_thickness": revise,
        "production_orders": production_orders,
        "samples": samples,
    }


@router.get("/reports/po-order-description")
def report_po_order_description(
    db: Session = Depends(get_db),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    customer: Optional[str] = Query(None, description="Nama / kode customer (snapshot)"),
    date_field: str = Query(
        "order",
        description="Saring rentang tanggal: order (order_date), created (created_at header), either (salah satu)",
    ),
    _user=Depends(get_current_user),
) -> dict[str, Any]:
    """Data LAPORAN PO HARIAN MARKETING: revisi ketebalan, production order, sample — format lembar Excel."""
    _ = _user
    return _build_marketing_daily_payload(db, date_from, date_to, customer, date_field)


_MARKETING_CSV_COLS = [
    "section",
    "order_date",
    "thi_line_ref",
    "customer",
    "brand",
    "order_type",
    "po_no",
    "po_customer_ref",
    "material",
    "thickness",
    "old_thickness",
    "new_thickness",
    "emboss",
    "softness_type",
    "pu_production",
    "color",
    "softness",
    "qty",
    "unit_price",
    "color_reference",
    "backing",
    "model",
    "style_article",
    "line_etd",
    "buyer",
    "po_status",
    "po_category",
]


def _row_to_csv_tuple(section: str, row: dict[str, Any]) -> tuple:
    return (
        section,
        row.get("order_date") or "",
        row.get("thi_line_ref") or "",
        row.get("customer") or "",
        row.get("brand") or "",
        row.get("order_type") or "",
        row.get("poNo") or "",
        row.get("po_customer_ref") or "",
        row.get("material") or "",
        row.get("thickness") or "",
        row.get("oldThickness") or "",
        row.get("newThickness") or "",
        row.get("emboss") or "",
        row.get("softness_type") or "",
        row.get("pu_production") or "",
        row.get("color") or "",
        row.get("softness") or "",
        row.get("qty", ""),
        row.get("unit_price") or "",
        row.get("color_reference") or "",
        row.get("backing") or "",
        row.get("model") or "",
        row.get("style_article") or "",
        row.get("line_etd") or "",
        row.get("buyer") or "",
        row.get("status") or "",
        row.get("po_category") or "",
    )


@router.get("/reports/po-daily-marketing.csv")
def export_po_daily_marketing_csv(
    db: Session = Depends(get_db),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    customer: Optional[str] = Query(None),
    date_field: str = Query("order"),
    _user=Depends(get_current_user),
) -> Response:
    """Ekspor CSV (UTF-8 BOM) selaras LAPORAN PO HARIAN MARKETING — tiga blok + kolom lengkap."""
    _ = _user
    payload = _build_marketing_daily_payload(db, date_from, date_to, customer, date_field)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(_MARKETING_CSV_COLS)
    for row in payload["revise_thickness"]:
        w.writerow(_row_to_csv_tuple("REVISE_THICKNESS", row))
    for row in payload["production_orders"]:
        w.writerow(_row_to_csv_tuple("PRODUCTION_ORDER", row))
    for row in payload["samples"]:
        w.writerow(_row_to_csv_tuple("SAMPLE", row))

    fn = f"laporan_po_harian_marketing_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.csv"
    body = "\ufeff" + buf.getvalue()
    return Response(
        content=body,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{fn}"'},
    )


@router.get("/reports/po-daily-recap.csv")
def export_po_daily_recap_csv(
    report_date: Optional[date] = Query(None, alias="date"),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
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
def export_sales_orders_csv(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> Response:
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
def export_so_lines_csv(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> Response:
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
