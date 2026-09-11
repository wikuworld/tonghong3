"""Nomor dokumen berjalan (produksi / packing / quotation).

Catatan: nomor Sales Order (PO) memakai ``app.services.so_numbering`` (format marketing).
Modul ini tetap dipakai untuk PRD/PACK/QUO berbasis periode ``PREFIX-YYYYMM-NNNNN``.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DocumentSequence
from app.timeutil import app_now_aware


def _period() -> str:
    return app_now_aware().strftime("%Y%m")


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
