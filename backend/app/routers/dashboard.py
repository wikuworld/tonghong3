"""Dashboard ringkasan (CR §3.7) — KPI + grafik & feed dari data aktual."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import (
    DeliveryHeader,
    ExchangeRate,
    Invoice,
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


@router.get("/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db)) -> dict[str, Any]:
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

    rate = db.scalars(
        select(ExchangeRate).order_by(ExchangeRate.effective_date.desc()).limit(1)
    ).first()

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
        "as_of": date.today().isoformat(),
    }
