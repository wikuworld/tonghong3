"""Dashboard ringkasan (CR §3.7) — KPI + grafik & feed dari data aktual."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends
from sqlalchemy import and_, func, select
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session

from app.db import get_db
from app.routers.auth import get_current_user
from app.models import (
    Customer,
    DeliveryHeader,
    DeliveryDetail,
    ExchangeRate,
    Invoice,
    PoDetail,
    PoHeader,
    ProductionOrder,
    QcDetail,
)

router = APIRouter(tags=["dashboard"])


def _count_trend_by_created_date(
    db: Session, model, day: date
) -> int:
    """Hitung baris dengan DATE(created_at) = day (MySQL)."""
    return (
        db.scalar(
            select(func.count())
            .select_from(model)
            .where(func.date(model.created_at) == day)  # type: ignore[arg-type]
        )
        or 0
    )


def _build_activity_feed(db: Session) -> list[dict[str, Any]]:
    events: list[tuple[Optional[datetime], str, str, Optional[str]]] = []

    for h in db.scalars(select(PoHeader).order_by(PoHeader.id.desc()).limit(8)):
        dt = h.updated_at or h.created_at
        events.append(
            (dt, "po", (h.po_number or f"SO-{h.id}"), h.status)
        )

    for p in db.scalars(select(ProductionOrder).order_by(ProductionOrder.id.desc()).limit(6)):
        events.append(
            (p.created_at, "prod", (p.production_number or f"PRD-{p.id}"), p.status)
        )

    for d in db.scalars(select(DeliveryHeader).order_by(DeliveryHeader.id.desc()).limit(6)):
        events.append(
            (d.created_at, "del", (d.delivery_number or f"DN-{d.id}"), d.status)
        )

    def sort_key(x: tuple) -> datetime:
        dt = x[0]
        if dt is None:
            return datetime.min
        return dt

    events.sort(key=sort_key, reverse=True)

    out: list[dict[str, Any]] = []
    for dt, kind, ref, st in events[:12]:
        if dt is None:
            continue
        out.append(
            {
                "occurred_at": dt.isoformat(timespec="seconds"),
                "kind": kind,
                "ref": ref,
                "status": st or "",
            }
        )
    return out


def _build_rcvd_po_summary(db: Session) -> dict[str, Any]:
    """
    Ringkasan RCVD PO berbasis data real PO:
    - sumber qty: po_details.quantity_order (sf)
    - kategori: po_headers.po_category == 'suede' => SUEDE, selain itu => PU
    - tanggal acuan: order_date terbaru yang punya detail qty
    """
    as_of = db.scalar(
        select(func.max(PoHeader.order_date))
        .select_from(PoHeader)
        .join(PoDetail, PoDetail.po_id == PoHeader.id)
        .where(PoHeader.order_date.is_not(None))
    )
    if not as_of:
        return {
            "as_of": None,
            "pu_lines": [],
            "suede_lines": [],
            "total_pu_sf": 0.0,
            "total_suede_sf": 0.0,
        }

    rows = db.execute(
        select(
            PoHeader.po_category,
            PoHeader.buyer,
            PoHeader.customer_name_snapshot,
            func.coalesce(func.sum(PoDetail.quantity_order), 0),
        )
        .join(PoDetail, PoDetail.po_id == PoHeader.id)
        .where(PoHeader.order_date == as_of)
        .group_by(PoHeader.po_category, PoHeader.buyer, PoHeader.customer_name_snapshot)
        .order_by(PoHeader.buyer.asc(), PoHeader.customer_name_snapshot.asc())
    ).all()

    pu_lines: list[dict[str, Any]] = []
    suede_lines: list[dict[str, Any]] = []
    total_pu = 0.0
    total_suede = 0.0

    for po_category, buyer, factory, qty in rows:
        qty_f = float(qty or 0)
        if qty_f <= 0:
            continue
        line = {
            "buyer": str(buyer or "").strip() or "-",
            "factory": str(factory or "").strip() or "-",
            "sf": qty_f,
        }
        if str(po_category or "").strip().lower() == "suede":
            suede_lines.append(line)
            total_suede += qty_f
        else:
            pu_lines.append(line)
            total_pu += qty_f

    return {
        "as_of": as_of.isoformat(),
        "pu_lines": pu_lines,
        "suede_lines": suede_lines,
        "total_pu_sf": round(total_pu, 2),
        "total_suede_sf": round(total_suede, 2),
    }


def _delivery_status_label(status: str) -> str:
    s = (status or "").strip().lower()
    mapping = {
        "sent": "Received",
        "loading": "Loading",
        "ready_pickup": "Will be pick up",
        "pickup_ready": "Will be pick up",
        "picked_up": "Already pick up",
        "pickedup": "Already pick up",
        "draft": "Draft",
    }
    return mapping.get(s, status or "-")


def _build_delivery_digest(db: Session) -> dict[str, Any]:
    date_rows = db.execute(
        select(DeliveryHeader.delivery_date)
        .where(DeliveryHeader.delivery_date.is_not(None))
        .group_by(DeliveryHeader.delivery_date)
        .order_by(DeliveryHeader.delivery_date.desc())
        .limit(2)
    ).all()
    dates = [row[0] for row in date_rows if row[0]]
    out_days: list[dict[str, Any]] = []
    for d in dates:
        rows = db.execute(
            select(
                Customer.code,
                Customer.name,
                DeliveryHeader.status,
                func.coalesce(func.sum(DeliveryDetail.qty), 0),
            )
            .select_from(DeliveryHeader)
            .join(Customer, Customer.id == DeliveryHeader.customer_id, isouter=True)
            .join(DeliveryDetail, DeliveryDetail.delivery_id == DeliveryHeader.id, isouter=True)
            .where(DeliveryHeader.delivery_date == d)
            .group_by(Customer.code, Customer.name, DeliveryHeader.status)
            .order_by(Customer.code.asc(), Customer.name.asc())
        ).all()
        lines: list[dict[str, Any]] = []
        total_sf = 0.0
        for code, name, status, qty in rows:
            sf = float(qty or 0)
            if sf <= 0:
                continue
            lines.append(
                {
                    "customer_code": str(code or "").strip() or str(name or "").strip() or "-",
                    "customer_name": str(name or "").strip() or "-",
                    "sf": sf,
                    "status_label": _delivery_status_label(str(status or "").strip()),
                }
            )
            total_sf += sf
        out_days.append(
            {
                "date": d.isoformat(),
                "lines": lines,
                "total_sf": round(total_sf, 2),
            }
        )
    return {"days": out_days}


@router.get("/dashboard/invoice-summary")
def invoice_summary(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> dict[str, Any]:
    """Ringkasan invoice berdasarkan FK relationships."""
    from app.models import Customer
    
    total_invoices = db.scalar(select(func.count()).select_from(Invoice)) or 0
    total_amount = db.scalar(
        select(func.coalesce(func.sum(Invoice.total_amount), 0)).select_from(Invoice)
    ) or 0
    
    paid_invoices = db.scalar(
        select(func.count()).select_from(Invoice).where(Invoice.payment_status == "paid")
    ) or 0
    paid_amount = db.scalar(
        select(func.coalesce(func.sum(Invoice.total_amount), 0))
        .select_from(Invoice)
        .where(Invoice.payment_status == "paid")
    ) or 0
    
    unpaid_invoices = db.scalar(
        select(func.count()).select_from(Invoice).where(Invoice.payment_status == "unpaid")
    ) or 0
    unpaid_amount = db.scalar(
        select(func.coalesce(func.sum(Invoice.total_amount), 0))
        .select_from(Invoice)
        .where(Invoice.payment_status == "unpaid")
    ) or 0
    
    overdue_invoices = db.scalar(
        select(func.count())
        .select_from(Invoice)
        .where(
            and_(
                Invoice.payment_status == "unpaid",
                Invoice.due_date < date.today(),
            )
        )
    ) or 0
    overdue_amount = db.scalar(
        select(func.coalesce(func.sum(Invoice.total_amount), 0))
        .select_from(Invoice)
        .where(
            and_(
                Invoice.payment_status == "unpaid",
                Invoice.due_date < date.today(),
            )
        )
    ) or 0
    
    invoices_by_customer = db.execute(
        select(Customer.name, func.count(Invoice.id), func.coalesce(func.sum(Invoice.total_amount), 0))
        .join(Invoice, Invoice.customer_id == Customer.id)
        .group_by(Customer.id, Customer.name)
        .order_by(func.sum(Invoice.total_amount).desc())
        .limit(10)
    ).all()
    
    top_customers = [
        {"customer_name": str(row[0] or "Unknown"), "invoice_count": int(row[1]), "total_amount": float(row[2])}
        for row in invoices_by_customer
    ]
    
    return {
        "total_invoices": total_invoices,
        "total_amount": float(total_amount),
        "paid_invoices": paid_invoices,
        "paid_amount": float(paid_amount),
        "unpaid_invoices": unpaid_invoices,
        "unpaid_amount": float(unpaid_amount),
        "overdue_invoices": overdue_invoices,
        "overdue_amount": float(overdue_amount),
        "top_customers": top_customers,
        "as_of": date.today().isoformat(),
    }


@router.get("/dashboard/summary")
def dashboard_summary(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> dict[str, Any]:
    n_so = db.scalar(select(func.count()).select_from(PoHeader)) or 0
    n_so_open = db.scalar(
        select(func.count()).select_from(PoHeader).where(
            PoHeader.status.in_(("draft", "confirmed", "production"))
        )
    ) or 0
    n_so_active = db.scalar(
        select(func.count()).select_from(PoHeader).where(PoHeader.status != "draft")
    ) or 0
    n_prod = db.scalar(select(func.count()).select_from(ProductionOrder)) or 0
    n_prod_in_progress = db.scalar(
        select(func.count())
        .select_from(ProductionOrder)
        .where(ProductionOrder.status == "in_progress")
    ) or 0
    n_delivery = db.scalar(select(func.count()).select_from(DeliveryHeader)) or 0
    n_invoice = db.scalar(select(func.count()).select_from(Invoice)) or 0
    n_qc_reject = db.scalar(
        select(func.count()).select_from(QcDetail).where(QcDetail.is_ok.is_(False))
    ) or 0
    n_qc_ok = db.scalar(
        select(func.count()).select_from(QcDetail).where(QcDetail.is_ok.is_(True))
    ) or 0
    n_qc_total = db.scalar(select(func.count()).select_from(QcDetail)) or 0

    rate = None
    try:
        rate = db.scalars(
            select(ExchangeRate).order_by(ExchangeRate.effective_date.desc()).limit(1)
        ).first()
    except ProgrammingError:
        # Tabel exchange_rates belum ada / belum di-migrate — jangan gagalkan seluruh dashboard.
        db.rollback()
        rate = None

    today = date.today()
    trend_labels: list[str] = []
    trend_prod: list[int] = []
    trend_del: list[int] = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        trend_labels.append(d.isoformat())
        trend_prod.append(_count_trend_by_created_date(db, ProductionOrder, d))
        trend_del.append(_count_trend_by_created_date(db, DeliveryHeader, d))

    # Komposisi PO per po_category
    cat_rows = db.execute(
        select(PoHeader.po_category, func.count())
        .group_by(PoHeader.po_category)
    ).all()
    po_by_category: list[dict[str, Any]] = [
        {"category": str(row[0] or "production"), "count": int(row[1])}
        for row in cat_rows
        if row[1]
    ]
    po_by_category.sort(key=lambda x: -x["count"])

    # Pipeline: jumlah entitas per tahap (perbandingan relatif)
    pipeline = {
        "po_total": n_so,
        "production_orders": n_prod,
        "qc_ok_lines": n_qc_ok,
        "deliveries": n_delivery,
        "invoices": n_invoice,
    }

    # Monitoring (persentase sederhana)
    qc_pass_pct: Optional[float] = None
    if n_qc_total > 0:
        qc_pass_pct = round(100.0 * n_qc_ok / n_qc_total, 1)

    prod_active_pct: Optional[float] = None
    if n_prod > 0:
        prod_active_pct = round(100.0 * n_prod_in_progress / n_prod, 1)

    so_pipeline_pct: Optional[float] = None
    if n_so > 0:
        so_pipeline_pct = round(100.0 * n_so_active / n_so, 1)

    delivery_vs_so_pct: Optional[float] = None
    if n_so > 0:
        delivery_vs_so_pct = min(100.0, round(100.0 * n_delivery / n_so, 1))

    rcvd_po = _build_rcvd_po_summary(db)
    delivery_digest = _build_delivery_digest(db)

    return {
        "counts": {
            "sales_orders": n_so,
            "sales_orders_open": n_so_open,
            "production_orders": n_prod,
            "production_in_progress": n_prod_in_progress,
            "deliveries": n_delivery,
            "invoices": n_invoice,
            "qc_reject_lines": n_qc_reject,
            "qc_ok_lines": n_qc_ok,
            "qc_total_lines": n_qc_total,
        },
        "exchange_rate": (
            {
                "idr_per_usd": float(rate.idr_per_usd),
                "effective_date": rate.effective_date.isoformat(),
            }
            if rate
            else None
        ),
        "trend_7d": {
            "labels": trend_labels,
            "production_orders_per_day": trend_prod,
            "deliveries_per_day": trend_del,
        },
        "po_by_category": po_by_category,
        "pipeline": pipeline,
        "activity_feed": _build_activity_feed(db),
        "monitoring": {
            "so_pipeline_pct": so_pipeline_pct,
            "production_active_pct": prod_active_pct,
            "qc_pass_pct": qc_pass_pct,
            "delivery_coverage_pct": delivery_vs_so_pct,
        },
        "rcvd_po": rcvd_po,
        "delivery_digest": delivery_digest,
        "as_of": date.today().isoformat(),
    }
