"""Nomor dokumen berjalan (SO / produksi / packing)."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DocumentSequence


def _period() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m")


def next_number(db: Session, doc_type: str, prefix: str) -> str:
    """Contoh: SO-202604-00001, PRD-202604-00001, PACK-202604-00001."""
    period = _period()
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
        n = seq.last_value
        db.flush()
    return f"{prefix}-{period}-{n:05d}"
