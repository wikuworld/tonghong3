"""Pemilihan list harga buyer berdasarkan periode, plus cek tumpang tindih."""

from __future__ import annotations

from datetime import date
from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Brand, BrandBuyerMap, BuyerPriceList


def _code(value: Optional[str]) -> str:
    return (value or "").strip().upper()


def _as_date(value: Any) -> Optional[date]:
    if isinstance(value, date):
        return value
    return None


def ranges_overlap(a_start: date, a_end: date, b_start: date, b_end: date) -> bool:
    return a_start <= b_end and b_start <= a_end


def assert_period_bounds(period_start: Optional[date], period_end: Optional[date]) -> None:
    if period_start is None or period_end is None:
        raise HTTPException(status_code=400, detail="Tanggal mulai dan tanggal akhir periode wajib diisi")
    if period_end < period_start:
        raise HTTPException(status_code=400, detail="Tanggal akhir tidak boleh sebelum tanggal mulai")


def assert_brand_buyer(db: Session, brand_id: int, buyer_code: str) -> tuple[Brand, str]:
    brand = db.get(Brand, brand_id)
    if not brand:
        raise HTTPException(status_code=400, detail="Brand tidak ditemukan di master brand")
    code = _code(buyer_code)
    if not code:
        raise HTTPException(status_code=400, detail="Kode buyer wajib diisi")
    maps = db.scalars(select(BrandBuyerMap).where(BrandBuyerMap.brand_id == brand_id)).all()
    codes = {_code(row.buyer_code) for row in maps if _code(row.buyer_code)}
    if not codes:
        raise HTTPException(
            status_code=400,
            detail="Brand belum punya mapping buyer. Isi mapping di Master Brand terlebih dahulu.",
        )
    if code not in codes:
        raise HTTPException(status_code=400, detail=f"Buyer {code} tidak terhubung ke brand ini")
    return brand, code


def _period_text(row: BuyerPriceList) -> str:
    start = row.period_start.isoformat() if isinstance(row.period_start, date) else "?"
    end = row.period_end.isoformat() if isinstance(row.period_end, date) else "?"
    label = (row.period_label or "").strip()
    if label:
        return f"{label} ({start}–{end})"
    return f"{start}–{end}"


def assert_no_period_overlap(
    db: Session,
    *,
    brand_id: Optional[int],
    buyer_code: str,
    period_start: date,
    period_end: date,
    exclude_id: Optional[int] = None,
    brand_label: Optional[str] = None,
) -> None:
    code = _code(buyer_code)
    stmt = select(BuyerPriceList).where(BuyerPriceList.buyer_code == code)
    if brand_id is None:
        stmt = stmt.where(BuyerPriceList.brand_id.is_(None))
    else:
        stmt = stmt.where(BuyerPriceList.brand_id == brand_id)
    if exclude_id is not None:
        stmt = stmt.where(BuyerPriceList.id != exclude_id)
    for other in db.scalars(stmt).all():
        start = _as_date(other.period_start)
        end = _as_date(other.period_end)
        if start is None or end is None:
            continue
        if ranges_overlap(period_start, period_end, start, end):
            who = (brand_label or code).strip() or code
            raise HTTPException(
                status_code=409,
                detail=f"Periode bentrok dengan list {who} {_period_text(other)}",
            )


def pick_price_list(lists: list[Any], as_of: Optional[date]) -> Any | None:
    """Pilih list yang periodenya mencakup tanggal, lalu cadangan tanpa tanggal."""
    when = as_of or date.today()
    covering: list[Any] = []
    legacy: list[Any] = []
    for row in lists:
        start = _as_date(getattr(row, "period_start", None))
        end = _as_date(getattr(row, "period_end", None))
        if start is None and end is None:
            legacy.append(row)
            continue
        if start is not None and end is not None and start <= when <= end:
            covering.append(row)
    if covering:
        covering.sort(key=lambda row: _as_date(row.period_start) or date.min, reverse=True)
        return covering[0]
    if legacy:
        return legacy[0]
    return None


def select_buyer_price_list(db: Session, buyer_code: str, as_of: Optional[date]) -> Any | None:
    code = _code(buyer_code)
    if not code:
        return None
    lists = list(
        db.scalars(select(BuyerPriceList).where(BuyerPriceList.buyer_code == code)).all()
    )
    return pick_price_list(lists, as_of)


def unique_brand_id_for_buyer(db: Session, buyer_code: str) -> Optional[int]:
    code = _code(buyer_code)
    if not code:
        return None
    ids = {
        int(brand_id)
        for brand_id in db.scalars(
            select(BrandBuyerMap.brand_id).where(BrandBuyerMap.buyer_code == code)
        ).all()
        if brand_id is not None
    }
    if len(ids) == 1:
        return next(iter(ids))
    return None


def find_list_same_period(
    db: Session,
    buyer_code: str,
    period_start: Optional[date],
    period_end: Optional[date],
) -> Any | None:
    code = _code(buyer_code)
    stmt = select(BuyerPriceList).where(BuyerPriceList.buyer_code == code)
    if period_start is None and period_end is None:
        stmt = stmt.where(
            BuyerPriceList.period_start.is_(None),
            BuyerPriceList.period_end.is_(None),
        )
    else:
        stmt = stmt.where(
            BuyerPriceList.period_start == period_start,
            BuyerPriceList.period_end == period_end,
        )
    return db.scalars(stmt).first()
