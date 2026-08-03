"""Buyer code registry helpers (master integrity F1)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    BrandBuyerMap,
    BuyerCode,
    BuyerPriceList,
)

_HARDCODE = frozenset(
    {"GLOBAL", "NB", "ADIDAS", "UA", "NIKE", "PUMA", "REEBOK", "OIA", "OIA NIKE"}
)


def list_active_buyer_codes(db: Session) -> list[str]:
    """Union registry + fallback sources (non-breaking)."""
    codes: set[str] = set(_HARDCODE)
    for row in db.scalars(select(BuyerCode).where(BuyerCode.is_active.is_(True))).all():
        if row.code:
            codes.add(str(row.code).strip().upper())
    # fallback jika tabel masih kosong / belum migrasi di env lain
    for src in (
        db.scalars(select(BuyerPriceList.buyer_code)).all(),
        db.scalars(select(BrandBuyerMap.buyer_code).distinct()).all(),
    ):
        for c in src:
            if c:
                codes.add(str(c).strip().upper())
    return sorted(codes)


def ensure_buyer_code(db: Session, code: str) -> BuyerCode | None:
    c = (code or "").strip().upper()
    if not c:
        return None
    row = db.scalars(select(BuyerCode).where(BuyerCode.code == c)).first()
    if row:
        return row
    row = BuyerCode(code=c, name=c, is_active=True)
    db.add(row)
    db.flush()
    return row


def collect_unknown_buyer_codes(db: Session, candidates: list[str]) -> list[str]:
    known = set(list_active_buyer_codes(db))
    out: list[str] = []
    for raw in candidates:
        c = (raw or "").strip().upper()
        if c and c not in known:
            out.append(c)
    return sorted(set(out))
