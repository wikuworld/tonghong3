"""Normalisasi ketebalan PO/master ke format rentang standar (1.2-1.4)."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Any

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


def _normalize_decimal_token(raw: str) -> str:
    """Terima pemisah desimal koma (1,5) selain titik."""
    s = str(raw).strip()
    if re.fullmatch(r"\d,\d+", s):
        return s.replace(",", ".", 1)
    return s


def _to_decimal(raw: str | None) -> Decimal | None:
    if raw is None:
        return None
    s = _normalize_decimal_token(str(raw).strip())
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
    if raw in {"-", "—", "–"}:
        return ""
    if re.fullmatch(r"\d,\d+", raw):
        raw = raw.replace(",", ".", 1)
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
    raw = str(text or "").strip()
    # Buang satuan agar parsing rentang tetap jalan (1.2-1.4MM → 1.2-1.4).
    raw = re.sub(r"(?i)\s*mm\s*$", "", raw).strip()
    canon = canonical_thickness_range(raw)
    if not canon:
        return ""
    if "-" in canon:
        left, right = canon.split("-", 1)
        return f"{left} - {right}"
    return canon


def display_thickness_with_mm(text: str | None) -> str:
    """Tampilan dokumen (invoice/SJ/PI/dll): '1.2 - 1.4 mm'."""
    disp = display_thickness_range(text)
    if not disp:
        return ""
    return f"{disp} mm"


def thickness_from_po_detail(pod: Any | None) -> str:
    """Ambil teks ketebalan mentah dari PoDetail (tanpa satuan)."""
    if pod is None:
        return ""
    text = getattr(pod, "thickness_text", None)
    if text is not None and str(text).strip():
        return str(text).strip()
    a = getattr(pod, "thickness_min", None)
    b = getattr(pod, "thickness_max", None)
    if a is not None and b is not None:
        return f"{a}-{b}"
    if a is not None or b is not None:
        return str(a if a is not None else b)
    return ""


def display_po_thickness_mm(pod: Any | None) -> str:
    """Ketebalan PoDetail untuk cetakan, selalu dengan satuan mm."""
    return display_thickness_with_mm(thickness_from_po_detail(pod))


def thickness_ranges_equivalent(a: str | None, b: str | None) -> bool:
    ca = canonical_thickness_range(a)
    cb = canonical_thickness_range(b)
    if not ca or not cb:
        return False
    if ca == cb:
        return True
    # Fallback: bandingkan token numerik tanpa spasi
    return ca.replace(" ", "") == cb.replace(" ", "")
