"""Generator nomor SO (Sales Order): prefix per kategori + YYMMDD + seq harian 2 digit."""

from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DocumentSequence

# Selaras format marketing: Production=PS, Sample=S, Claim=PSC, Return prod=PSR, Return sample=SR, PU Coated=THIPM.
_SO_PREFIX_BY_CATEGORY: dict[str, str] = {
    "production": "PS",
    "sample": "S",
    "claim": "PSC",
    "return": "PSR",
    "subcont": "PS",
    "suede": "PS",
}


def so_prefix_for_po(
    *,
    po_category: str,
    order_type_label: str | None = None,
    material_group: str | None = None,
) -> str:
    cat = (po_category or "production").strip().lower()
    ol = (order_type_label or "").upper()
    mg = (material_group or "").strip().lower()

    if cat == "sample":
        return "S"
    if cat == "claim":
        return "PSC"
    if cat == "return":
        if "SAMPLE" in ol:
            return "SR"
        return "PSR"
    if cat == "production" and mg == "pu":
        return "THIPM"
    return _SO_PREFIX_BY_CATEGORY.get(cat, "PS")


def _resolve_at(*, order_date: date | None = None, at: datetime | None = None) -> datetime:
    if at is not None:
        return at
    if order_date is not None:
        return datetime.combine(order_date, datetime.min.time())
    return datetime.now(timezone.utc)


def _sequence_key(prefix: str, at: datetime) -> tuple[str, str, str]:
    period = at.strftime("%Y%m%d")
    yymmdd = at.strftime("%y%m%d")
    doc_type = f"SO:{prefix}"
    return doc_type, period, yymmdd


def format_so_number(*, prefix: str, at: datetime, seq_value: int) -> str:
    _, _, yymmdd = _sequence_key(prefix, at)
    return f"{prefix}{yymmdd}{seq_value:02d}"


def peek_so_number(
    db: Session,
    *,
    po_category: str,
    order_type_label: str | None = None,
    material_group: str | None = None,
    order_date: date | None = None,
    at: datetime | None = None,
) -> str:
    """Preview nomor SO berikutnya tanpa increment sequence."""
    prefix = so_prefix_for_po(
        po_category=po_category,
        order_type_label=order_type_label,
        material_group=material_group,
    )
    dt = _resolve_at(order_date=order_date, at=at)
    doc_type, period, _ = _sequence_key(prefix, dt)
    seq = db.scalars(
        select(DocumentSequence).where(
            DocumentSequence.doc_type == doc_type,
            DocumentSequence.period == period,
        )
    ).first()
    n = (int(seq.last_value) + 1) if seq else 1
    return format_so_number(prefix=prefix, at=dt, seq_value=n)


def next_so_number(
    db: Session,
    *,
    po_category: str,
    order_type_label: str | None = None,
    material_group: str | None = None,
    order_date: date | None = None,
    at: datetime | None = None,
) -> str:
    """Alokasi nomor SO berikutnya (increment sequence harian per prefix)."""
    prefix = so_prefix_for_po(
        po_category=po_category,
        order_type_label=order_type_label,
        material_group=material_group,
    )
    dt = _resolve_at(order_date=order_date, at=at)
    doc_type, period, _ = _sequence_key(prefix, dt)
    seq = db.scalars(
        select(DocumentSequence)
        .where(
            DocumentSequence.doc_type == doc_type,
            DocumentSequence.period == period,
        )
        .with_for_update()
    ).first()
    if seq is None:
        seq = DocumentSequence(doc_type=doc_type, period=period, last_value=1)
        db.add(seq)
        db.flush()
        n = 1
    else:
        seq.last_value += 1
        n = int(seq.last_value)
        db.flush()
    return format_so_number(prefix=prefix, at=dt, seq_value=n)
