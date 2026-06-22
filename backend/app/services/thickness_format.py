"""Normalisasi ketebalan PO/master ke format rentang standar (1.2-1.4)."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

# Selaras opsi master item & master harga
STANDARD_THICKNESS_BUCKETS: list[tuple[Decimal, Decimal, str]] = [
    (Decimal("1.0"), Decimal("1.2"), "1.0-1.2"),
    (Decimal("1.2"), Decimal("1.4"), "1.2-1.4"),
    (Decimal("1.4"), Decimal("1.6"), "1.4-1.6"),
    (Decimal("1.6"), Decimal("1.8"), "1.6-1.8"),
]

_RANGE_RE = re.compile(
    r"^\s*([\d.]+)\s*[-–]\s*([\d.]+)\s*$",
)


def _to_decimal(raw: str | None) -> Decimal | None:
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return None


def single_value_to_bucket(value: Decimal) -> str:
    for lo, hi, label in STANDARD_THICKNESS_BUCKETS:
        if lo <= value <= hi:
            return label
    return format(value.normalize(), "f").rstrip("0").rstrip(".")


def canonical_thickness_range(text: str | None) -> str:
    """Normalisasi ke label kanonik tanpa spasi: 1.2-1.4."""
    raw = str(text or "").strip()
    if not raw:
        return ""

    m = _RANGE_RE.match(raw)
    if m:
        lo = _to_decimal(m.group(1))
        hi = _to_decimal(m.group(2))
        if lo is not None and hi is not None:
            for blo, bhi, label in STANDARD_THICKNESS_BUCKETS:
                if lo == blo and hi == bhi:
                    return label
            lo_s = format(lo.normalize(), "f").rstrip("0").rstrip(".")
            hi_s = format(hi.normalize(), "f").rstrip("0").rstrip(".")
            return f"{lo_s}-{hi_s}"

    single = _to_decimal(raw)
    if single is not None:
        return single_value_to_bucket(single)

    return raw


def display_thickness_range(text: str | None) -> str:
    """Tampilan UI: 1.2 - 1.4 (spasi di sekitar strip)."""
    canon = canonical_thickness_range(text)
    if not canon:
        return ""
    if "-" in canon:
        left, right = canon.split("-", 1)
        return f"{left} - {right}"
    return canon


def thickness_ranges_equivalent(a: str | None, b: str | None) -> bool:
    ca = canonical_thickness_range(a)
    cb = canonical_thickness_range(b)
    if not ca or not cb:
        return False
    if ca == cb:
        return True
    # Fallback: bandingkan token numerik tanpa spasi
    return ca.replace(" ", "") == cb.replace(" ", "")
