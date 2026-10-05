"""Nomor Surat Jalan (THI-…) dan Invoice (THIN-…) sesuai kategori transaksi marketing."""

from __future__ import annotations

import re
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DocumentSequence, PoHeader
from app.timeutil import app_now_aware

# Kode setelah THI- / THIN- (boleh 1–2 huruf, mis. MD = Sample).
_CATEGORY_CODE: dict[str, str] = {
    "production": "M",
    "sample": "MD",
    "claim": "C",  # Compensate
    "return": "R",
    "subcont": "T",
    "suede": "M",
}

_SJ_PREFIX = "THI"
_INV_PREFIX = "THIN"

_LEGACY_DEL = re.compile(r"^DEL-(\d{6})-(\d+)$", re.IGNORECASE)
_LEGACY_INV = re.compile(r"^INV-(\d{6})-(\d+)$", re.IGNORECASE)
_THI_FORM = re.compile(r"^THI-([A-Za-z]{1,2})(\d{6})(\d{3,})$", re.IGNORECASE)
_THIN_FORM = re.compile(r"^THIN-([A-Za-z]{1,2})(\d{6})(\d{3,})$", re.IGNORECASE)
_IN_LEGACY_SWAP = re.compile(r"^IN-([A-Za-z]{1,2})(.+)$", re.IGNORECASE)


def category_code_for_po(ph: PoHeader | None) -> str:
    """Kode jenis transaksi: M / MD / C / R / T."""
    if not ph:
        return "M"
    ol = (ph.order_type_label or "").upper()
    if "FOC" in ol:
        return "MD"
    c = (ph.po_category or "production").lower()
    return _CATEGORY_CODE.get(c, "M")


def category_letter_for_po(ph: PoHeader | None) -> str:
    """Alias historis → sekarang mengembalikan kode (boleh multi-huruf)."""
    return category_code_for_po(ph)


def _yymmdd(on_date: date | None = None) -> str:
    d = on_date or app_now_aware().date()
    return d.strftime("%y%m%d")


def _next_daily_seq(db: Session, *, doc_type: str, period: str) -> int:
    """Seq harian per doc_type (mis. THI-M) + period YYMMDD. period max 10 char."""
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
        return 1
    seq.last_value += 1
    db.flush()
    return int(seq.last_value)


def allocate_surat_jalan_number(
    db: Session,
    *,
    po: PoHeader | None = None,
    on_date: date | None = None,
) -> str:
    """Format: THI-{kode}{YYMMDD}{XXX}."""
    code = category_code_for_po(po)
    ymd = _yymmdd(on_date)
    doc_type = f"{_SJ_PREFIX}-{code}"[:20]
    n = _next_daily_seq(db, doc_type=doc_type, period=ymd)
    return f"{_SJ_PREFIX}-{code}{ymd}{n:03d}"


def allocate_invoice_number(
    db: Session,
    *,
    po: PoHeader | None = None,
    on_date: date | None = None,
) -> str:
    """Format: THIN-{kode}{YYMMDD}{XXX}."""
    code = category_code_for_po(po)
    ymd = _yymmdd(on_date)
    doc_type = f"{_INV_PREFIX}-{code}"[:20]
    n = _next_daily_seq(db, doc_type=doc_type, period=ymd)
    return f"{_INV_PREFIX}-{code}{ymd}{n:03d}"


def _seq_from_legacy_tail(tail: str) -> str:
    try:
        n = int(tail)
    except ValueError:
        n = 1
    return f"{max(n, 1):03d}"[-3:].zfill(3) if n < 1000 else f"{n:03d}"[-3:]


def _remap_legacy(
    stored: str,
    *,
    prefix: str,
    code: str,
    doc_date: date | None,
) -> str | None:
    """DEL-/INV-YYYYMM-NNNNN → THI-/THIN-{code}{yymmdd}{XXX}."""
    if prefix == _SJ_PREFIX:
        m = _LEGACY_DEL.match(stored)
    else:
        m = _LEGACY_INV.match(stored)
    if not m:
        return None
    period_ym, tail = m.group(1), m.group(2)
    if doc_date is not None:
        ymd = doc_date.strftime("%y%m%d")
    else:
        # Period legacy YYYYMM → pakai hari 01 sebagai fallback
        ymd = period_ym[2:] + "01" if len(period_ym) == 6 else _yymmdd(None)
    return f"{prefix}-{code}{ymd}{_seq_from_legacy_tail(tail)}"


def _normalize_marketing_form(stored: str, *, prefix: str, code: str) -> str | None:
    """THI-/THIN- sudah benar → pastikan kode kategori sesuai PO."""
    pat = _THI_FORM if prefix == _SJ_PREFIX else _THIN_FORM
    m = pat.match(stored)
    if not m:
        return None
    ymd, seq = m.group(2), m.group(3)
    seq3 = seq[-3:].zfill(3) if len(seq) >= 3 else seq.zfill(3)
    return f"{prefix}-{code.upper()}{ymd}{seq3}"


def surat_jalan_display_number(
    stored: str,
    ph: PoHeader | None,
    *,
    doc_date: date | None = None,
) -> str:
    s = (stored or "").strip()
    if not s:
        return ""
    code = category_code_for_po(ph)
    norm = _normalize_marketing_form(s, prefix=_SJ_PREFIX, code=code)
    if norm:
        return norm
    legacy = _remap_legacy(s, prefix=_SJ_PREFIX, code=code, doc_date=doc_date)
    if legacy:
        return legacy
    # Pola lama THI-X… (1 huruf) — ganti kode
    m = re.match(r"^THI-([A-Za-z]+)(.+)$", s, re.IGNORECASE)
    if m:
        rest = m.group(2)
        if re.match(r"^\d{6}\d+", rest):
            return f"THI-{code}{rest}"
        return f"THI-{code}{rest}"
    return s


def invoice_display_number(
    stored: str,
    ph: PoHeader | None,
    *,
    doc_date: date | None = None,
) -> str:
    s = (stored or "").strip()
    if not s:
        return ""
    code = category_code_for_po(ph)
    norm = _normalize_marketing_form(s, prefix=_INV_PREFIX, code=code)
    if norm:
        return norm
    legacy = _remap_legacy(s, prefix=_INV_PREFIX, code=code, doc_date=doc_date)
    if legacy:
        return legacy
    # Pola lama IN-X…
    m = _IN_LEGACY_SWAP.match(s)
    if m:
        rest = m.group(2)
        return f"{_INV_PREFIX}-{code}{rest}"
    m2 = re.match(r"^THIN-([A-Za-z]+)(.+)$", s, re.IGNORECASE)
    if m2:
        return f"{_INV_PREFIX}-{code}{m2.group(2)}"
    return s
