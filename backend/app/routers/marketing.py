"""Endpoint format lembar marketing (outstanding) dari data PO aktual."""

from __future__ import annotations

import csv
import io
from collections import defaultdict
from decimal import Decimal
from enum import Enum
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query, Response
from openpyxl import Workbook
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models import (
    Customer,
    DeliveryDetail,
    DeliveryHeader,
    Invoice,
    InvoiceDetail,
    PoDetail,
    PoHeader,
    ProductionDetail,
)
from app.routers.auth import get_current_user
from app.services.document_numbers import invoice_display_number, surat_jalan_display_number

router = APIRouter(tags=["marketing"])


class BalanceFilter(str, Enum):
    """Filter baris berdasarkan saldo baris PO (kolom balance_qty)."""

    all = "all"
    exclude_zero = "exclude_zero"
    positive_only = "positive_only"


class ShipmentStatusFilter(str, Enum):
    """Filter baris berdasarkan sisa kirim (balance terhitung atau tersimpan)."""

    all = "all"
    sent = "sent"
    not_sent = "not_sent"


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


def _passes_balance_value(balance: Decimal | None, mode: BalanceFilter) -> bool:
    b = balance
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


def _delivery_line_amount(
    dd: DeliveryDetail,
    pod: Optional[PoDetail],
    invd: Optional[InvoiceDetail],
) -> Decimal | None:
    if invd is not None and invd.amount is not None:
        return invd.amount
    if dd.qty is not None and pod is not None and pod.unit_price is not None:
        return (dd.qty * pod.unit_price).quantize(Decimal("0.01"))
    return None


def _order_type_marketing(h: PoHeader) -> str:
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


def _remark_system_text(ln: PoDetail, delivered: Decimal, balance: Decimal) -> str:
    """Ringkasan otomatis dari angka baris & ETD (berubah saat input PO / kiriman berubah)."""
    parts: list[str] = []
    if ln.quantity_order is not None:
        parts.append(f"Order {_dec_str(ln.quantity_order)} SF")
    parts.append(f"Terkirim {_dec_str(delivered)}")
    parts.append(f"Saldo {_dec_str(balance)}")
    if ln.stock_wh_qty is not None:
        parts.append(f"StokWH {_dec_str(ln.stock_wh_qty)}")
    if ln.line_etd:
        parts.append(f"ETD {ln.line_etd.isoformat()}")
    return " | ".join(parts)


def _delivery_slots(ln: PoDetail) -> dict[str, Any]:
    by_seq: dict[int, Any] = {}
    for d in ln.delivery_schedules or []:
        by_seq[int(d.sequence_no)] = d
    out: dict[str, Any] = {}
    for i in range(1, 7):
        d = by_seq.get(i)
        out[f"delivery_{i}_qty"] = _dec_str(d.qty) if d and d.qty is not None else ""
        out[f"delivery_{i}_date"] = d.delivery_date.isoformat() if d and d.delivery_date else ""
    return out


def _latest_production_status_by_pod(db: Session, pod_ids: set[int]) -> dict[int, str]:
    if not pod_ids:
        return {}
    rows = db.execute(
        select(ProductionDetail.po_detail_id, ProductionDetail.id, ProductionDetail.status)
        .where(ProductionDetail.po_detail_id.in_(pod_ids))
        .order_by(ProductionDetail.id.asc())
    ).all()
    out: dict[int, str] = {}
    for pod_id, _pid, status in rows:
        if pod_id is None:
            continue
        out[int(pod_id)] = (status or "").strip()
    return out


def _line_to_row(
    h: PoHeader,
    ln: PoDetail,
    delivered: Decimal,
    balance: Decimal,
    production_status: str,
) -> dict[str, Any]:
    brand = (h.brand_name_snapshot or "").strip() or "—"
    cust = (h.customer_name_snapshot or h.customer_code or "").strip() or "—"
    thi = (ln.thi_line_ref or "").strip() or "—"
    row: dict[str, Any] = {
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
        "balance_qty": _dec_str(balance),
        "system_reference": (ln.system_reference or "").strip() or "",
        "detail_remark": (ln.detail_remark or "").strip() or "",
        "remark_system": _remark_system_text(ln, delivered, balance),
        "remark_marketing": (ln.marketing_outstanding_remark or "").strip() or "",
        "delivered_qty": _dec_str(delivered),
        "production_status": production_status or "",
        "po_id": h.id,
        "po_detail_id": ln.id,
        "po_status": h.status or "",
        "mkt_stage": h.mkt_workflow_stage or "",
    }
    row.update(_delivery_slots(ln))
    return row


def _query_outstanding_rows(
    db: Session,
    balance_filter: BalanceFilter = BalanceFilter.exclude_zero,
    computed_balance: bool = True,
    po_q: Optional[str] = None,
    shipment_status: ShipmentStatusFilter = ShipmentStatusFilter.all,
) -> list[dict[str, Any]]:
    """Baris dari PO yang belum completed (aliran outstanding marketing)."""
    headers = db.scalars(
        select(PoHeader)
        .options(
            selectinload(PoHeader.details).selectinload(PoDetail.delivery_schedules)
        )
        .order_by(PoHeader.id.desc())
    ).all()

    delivered_by_po_detail: dict[int, Decimal] = {}
    if computed_balance:
        rows = db.execute(
            select(ProductionDetail.po_detail_id, func.sum(DeliveryDetail.qty))
            .join(DeliveryDetail, DeliveryDetail.production_detail_id == ProductionDetail.id)
            .group_by(ProductionDetail.po_detail_id)
        ).all()
        for pod_id, total in rows:
            if pod_id is None:
                continue
            delivered_by_po_detail[int(pod_id)] = total or Decimal(0)

    po_needle = (po_q or "").strip().lower()
    pending: list[tuple[PoHeader, PoDetail, Decimal, Decimal]] = []

    for h in headers:
        if (h.status or "").lower() == "completed":
            continue
        if po_needle:
            pn = (h.po_number or "").lower()
            if po_needle not in pn:
                continue
        for ln in h.details or []:
            if computed_balance:
                delivered = delivered_by_po_detail.get(int(ln.id), Decimal(0))
                qty = ln.quantity_order or Decimal(0)
                bal = qty - delivered
                if not _passes_balance_value(bal, balance_filter):
                    continue
                if shipment_status == ShipmentStatusFilter.sent and bal > 0:
                    continue
                if shipment_status == ShipmentStatusFilter.not_sent and bal <= 0:
                    continue
                pending.append((h, ln, delivered, bal))
            else:
                if not _passes_balance_filter(ln, balance_filter):
                    continue
                bstore = ln.balance_qty
                if shipment_status == ShipmentStatusFilter.sent:
                    if bstore is None or bstore > 0:
                        continue
                elif shipment_status == ShipmentStatusFilter.not_sent:
                    if bstore is not None and bstore <= 0:
                        continue
                delivered = Decimal(0)
                bal = ln.balance_qty if ln.balance_qty is not None else Decimal(0)
                pending.append((h, ln, delivered, bal))

    pod_ids = {int(ln.id) for _, ln, _, _ in pending}
    prod_status = _latest_production_status_by_pod(db, pod_ids)

    out: list[dict[str, Any]] = []
    for h, ln, delivered, bal in pending:
        out.append(_line_to_row(h, ln, delivered, bal, prod_status.get(int(ln.id), "")))
    return out


# Kolom unduhan Excel (label mengikuti lembar marketing; tanpa id internal).
_OUTSTANDING_XLS_COLUMNS: list[tuple[str, str]] = [
    ("order_date", "DATE"),
    ("thi_order", "THI ORDER"),
    ("customer_name", "CUSTOMER NAME"),
    ("brand", "BRAND"),
    ("order_type", "ORDER TYPE"),
    ("no_po", "NO PO"),
    ("material_name", "MATERIAL NAME"),
    ("thickness", "THICKNESS"),
    ("emboss", "EMBOSS"),
    ("softness_type", "SOFTNESS TYPE"),
    ("color", "COLOR"),
    ("softness", "SOFTNESS"),
    ("qty_sf", "QTY (S/F)"),
    ("unit_price", "PRICE"),
    ("color_reference", "COLOR S/W"),
    ("backing", "BACKING"),
    ("model", "MODEL"),
    ("style_article", "ARTICLE"),
    ("rtd_text", "RTA"),
    ("line_etd", "REPLY ETD"),
    ("stock_wh_qty", "STOCK WH"),
    ("balance_qty", "BALANCE"),
    ("system_reference", "SYSTEM NO"),
    ("remark_system", "REMARK (SISTEM)"),
    ("remark_marketing", "REMARK (MARKETING)"),
    ("detail_remark", "CATATAN BARIS PO"),
    ("delivered_qty", "QTY TERKIRIM"),
    ("production_status", "STATUS PRODUKSI"),
    ("delivery_1_qty", "1st Qty"),
    ("delivery_1_date", "1st Date"),
    ("delivery_2_qty", "2nd Qty"),
    ("delivery_2_date", "2nd Date"),
    ("delivery_3_qty", "3rd Qty"),
    ("delivery_3_date", "3rd Date"),
    ("delivery_4_qty", "4th Qty"),
    ("delivery_4_date", "4th Date"),
    ("delivery_5_qty", "5th Qty"),
    ("delivery_5_date", "5th Date"),
    ("delivery_6_qty", "6th Qty"),
    ("delivery_6_date", "6th Date"),
]


def _outstanding_rows_to_xlsx_bytes(rows: list[dict[str, Any]]) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Outstanding"
    keys = [k for k, _ in _OUTSTANDING_XLS_COLUMNS]
    ws.append([label for _, label in _OUTSTANDING_XLS_COLUMNS])
    for r in rows:
        ws.append([r.get(k) for k in keys])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()


# Kolom unduhan Excel — selaras lembar «DELIVERY LIST DARI SISTEM» (label Indonesia).
_DELIVERY_LIST_XLS_COLUMNS: list[tuple[str, str]] = [
    ("surat_jalan_no", "NO SJ"),
    ("delivery_date", "TGL KIRIM"),
    ("factory_name", "FACTORY NAME"),
    ("system_no", "SYSTEM NO"),
    ("po_date", "PO DATE"),
    ("po_number", "PO NUMBER"),
    ("lot_no", "LOT NO"),
    ("thickness", "THICKNESS"),
    ("color", "COLOR"),
    ("material_type", "TYPE"),
    ("material_name", "MATERIAL NAME"),
    ("qty_po", "QTY PO"),
    ("unit_price", "UNIT PRICE"),
    ("qty_roll", "ROLL"),
    ("qty_pcs", "PCS"),
    ("qty_sf", "SF"),
    ("gross_weight", "GW"),
    ("net_weight", "NW"),
    ("amount", "AMOUNT"),
    ("color_std", "COLOR STD"),
    ("emboss", "EMBOSS"),
    ("buyer", "BUYER"),
    ("style_article", "STYLE"),
    ("model", "MODEL"),
    ("invoice_number", "INV NUMBER"),
    ("pi_no", "PI_NO"),
    ("remark", "REMARK"),
    ("order_type", "ORDER TYPE"),
    ("delivery_status", "STATUS DELIVERY"),
]


def _delivery_list_rows_to_xlsx_bytes(rows: list[dict[str, Any]]) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Delivery List"
    keys = [k for k, _ in _DELIVERY_LIST_XLS_COLUMNS]
    ws.append([label for _, label in _DELIVERY_LIST_XLS_COLUMNS])
    for r in rows:
        ws.append([r.get(k) for k in keys])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()


def _delivery_detail_to_row(
    dd: DeliveryDetail,
    dh: DeliveryHeader,
    pd: Optional[ProductionDetail],
    pod: Optional[PoDetail],
    ph: Optional[PoHeader],
    cust: Optional[Customer],
    inv: Optional[Invoice],
    invd: Optional[InvoiceDetail],
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

    sj_raw = (dh.delivery_number or "").strip()
    surat_jalan_no = surat_jalan_display_number(sj_raw, ph) if sj_raw else "—"
    inv_raw = (inv.invoice_number or "").strip() if inv else ""
    invoice_number = invoice_display_number(inv_raw, ph) if inv_raw else ""

    gw: Decimal | None = None
    nw: Decimal | None = None
    if invd is not None:
        if invd.gross_weight is not None:
            gw = invd.gross_weight
        if invd.net_weight is not None:
            nw = invd.net_weight
    if nw is None and dd.weight is not None:
        nw = dd.weight

    amt = _delivery_line_amount(dd, pod, invd)

    return {
        "surat_jalan_no": surat_jalan_no or "—",
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
        "gross_weight": _dec_str(gw) if gw is not None else "",
        "net_weight": _dec_str(nw) if nw is not None else "",
        "amount": _dec_str(amt) if amt is not None else "",
        "color_std": (pod.color_reference or "").strip() if pod else "",
        "emboss": (pod.emboss or "").strip() if pod else "",
        "buyer": (ph.buyer or "").strip() if ph else "",
        "style_article": (pod.style_article or "").strip() if pod else "",
        "model": (pod.model or "").strip() if pod else "",
        "invoice_number": invoice_number,
        "pi_no": (ph.po_customer_ref or "").strip() if ph else "",
        "remark": (
            (pod.detail_remark or "").strip()
            if pod and (pod.detail_remark or "").strip()
            else ((ph.remark or "").strip() if ph and (ph.remark or "").strip() else "")
        ),
        "order_type": _order_type_marketing(ph) if ph else "",
        "destination": (dh.destination or "").strip() if dh.destination else "",
        "delivery_id": dh.id,
        "delivery_detail_id": dd.id,
        "delivery_status": dh.status or "",
    }


def _query_delivery_lines_rows(db: Session, q: Optional[str] = None) -> list[dict[str, Any]]:
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

    inv_ids = [i.id for i in inv_by_delivery.values()]
    details_by_invoice: dict[int, list[InvoiceDetail]] = defaultdict(list)
    if inv_ids:
        idets = db.scalars(
            select(InvoiceDetail)
            .where(InvoiceDetail.invoice_id.in_(inv_ids))
            .order_by(InvoiceDetail.invoice_id.asc(), InvoiceDetail.id.asc())
        ).all()
        for d in idets:
            details_by_invoice[int(d.invoice_id)].append(d)

    line_index: dict[int, int] = defaultdict(int)
    out: list[dict[str, Any]] = []
    for dd, dh, pd, pod, ph, cust in raw:
        inv = inv_by_delivery.get(dh.id)
        invd: InvoiceDetail | None = None
        if inv:
            lst = details_by_invoice.get(int(inv.id), [])
            li = line_index[dh.id]
            if li < len(lst):
                invd = lst[li]
        line_index[dh.id] += 1
        out.append(_delivery_detail_to_row(dd, dh, pd, pod, ph, cust, inv, invd))

    if q and str(q).strip():
        qq = str(q).strip().lower()

        def _match(row: dict[str, Any]) -> bool:
            for v in row.values():
                if v is None:
                    continue
                if qq in str(v).lower():
                    return True
            return False

        out = [r for r in out if _match(r)]
    return out


@router.get("/marketing/outstanding-lines")
def marketing_outstanding_lines(
    db: Session = Depends(get_db),
    balance_filter: BalanceFilter = Query(
        default=BalanceFilter.exclude_zero,
        description="all: semua baris; exclude_zero: sembunyikan balance tepat 0; positive_only: hanya balance > 0",
    ),
    computed_balance: bool = Query(True, description="Hitung balance dari qty_order - qty_terkirim (delivery)"),
    po_q: Optional[str] = Query(
        None,
        description="Substring pencarian nomor PO (case-insensitive)",
    ),
    shipment_status: ShipmentStatusFilter = Query(
        default=ShipmentStatusFilter.all,
        description="all | sent (balance 0) | not_sent (balance > 0)",
    ),
    _user=Depends(get_current_user),
) -> list[dict[str, Any]]:
    return _query_outstanding_rows(
        db, balance_filter, computed_balance, po_q=po_q, shipment_status=shipment_status
    )


@router.get("/marketing/outstanding-lines.csv")
def marketing_outstanding_lines_csv(
    db: Session = Depends(get_db),
    balance_filter: BalanceFilter = Query(default=BalanceFilter.exclude_zero),
    computed_balance: bool = Query(True),
    po_q: Optional[str] = Query(None),
    shipment_status: ShipmentStatusFilter = Query(default=ShipmentStatusFilter.all),
    _user=Depends(get_current_user),
) -> Response:
    rows = _query_outstanding_rows(
        db, balance_filter, computed_balance, po_q=po_q, shipment_status=shipment_status
    )
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


@router.get("/marketing/outstanding-lines.xlsx")
def marketing_outstanding_lines_xlsx(
    db: Session = Depends(get_db),
    balance_filter: BalanceFilter = Query(default=BalanceFilter.exclude_zero),
    computed_balance: bool = Query(True),
    po_q: Optional[str] = Query(None),
    shipment_status: ShipmentStatusFilter = Query(default=ShipmentStatusFilter.all),
    _user=Depends(get_current_user),
) -> Response:
    rows = _query_outstanding_rows(
        db, balance_filter, computed_balance, po_q=po_q, shipment_status=shipment_status
    )
    data = _outstanding_rows_to_xlsx_bytes(rows)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="marketing_outstanding.xlsx"'},
    )


@router.get("/marketing/delivery-lines")
def marketing_delivery_lines(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Saring baris (substring, case-insensitive)"),
    _user=Depends(get_current_user),
) -> list[dict[str, Any]]:
    return _query_delivery_lines_rows(db, q=q)


@router.get("/marketing/delivery-lines.csv")
def marketing_delivery_lines_csv(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None),
    _user=Depends(get_current_user),
) -> Response:
    rows = _query_delivery_lines_rows(db, q=q)
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


@router.get("/marketing/delivery-lines.xlsx")
def marketing_delivery_lines_xlsx(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None),
    _user=Depends(get_current_user),
) -> Response:
    rows = _query_delivery_lines_rows(db, q=q)
    data = _delivery_list_rows_to_xlsx_bytes(rows)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="delivery_list_sistem.xlsx"'},
    )
