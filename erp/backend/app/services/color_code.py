"""Parse kode warna dari teks item / swatch (kurung, dual COLORO, qualifier)."""

from __future__ import annotations

import re
from typing import NamedTuple

_PAREN_TOKEN_RE = re.compile(r"\(([A-Za-z0-9][A-Za-z0-9._/\- ]{0,62})\)")
_COLORO_RE = re.compile(r"^\d{3}-\d{2}-\d{2}$")
_CSI_LIKE_RE = re.compile(r"^(NB[A-Z0-9\-]+|[A-Z0-9]{2,16})$", re.IGNORECASE)
_QUALIFIER_WORDS = frozenset(
    {
        "FLUORESCENT",
        "PEARLIZED",
        "METALLIC",
        "METTALIC",
        "TCX",
        "TPG",
        "COLORO",
    }
)


class DualColorCode(NamedTuple):
    alias_code: str
    csi_code: str | None


def extract_item_color_code(color: str | None) -> str | None:
    """BLACK (00A) → 00A; UNIVERSITY RED (65N) FLUORESCENT → 65N; 0AJ/6CD → None."""
    tokens = _PAREN_TOKEN_RE.findall(color or "")
    if not tokens:
        return None
    return tokens[0].strip().upper()


def extract_item_color_qualifier(color: str | None) -> str | None:
    """Suffix setelah kurung: FLUORESCENT / PEARLIZED / TCX."""
    raw = re.sub(r"\s+", " ", (color or "").strip())
    if ")" not in raw:
        return None
    after = raw.rsplit(")", 1)[-1].strip(" -")
    if not after:
        return None
    upper = after.upper()
    if upper in _QUALIFIER_WORDS:
        return upper
    first = upper.split()[0] if upper else ""
    return first if first in _QUALIFIER_WORDS else after or None


def parse_dual_color_code(raw: str | None) -> DualColorCode | None:
    """`124-91-00 (NB103)` → alias COLORO + kandidat kode CSI."""
    text = re.sub(r"\s+", " ", (raw or "").strip())
    if not text:
        return None
    m = re.fullmatch(
        r"([A-Za-z0-9][A-Za-z0-9._/\- ]{0,62})\s*\(([A-Za-z0-9][A-Za-z0-9._/\- ]{0,62})\)",
        text,
    )
    if not m:
        return None
    outer = m.group(1).strip().upper()
    inner = m.group(2).strip().upper()
    if inner in _QUALIFIER_WORDS:
        return DualColorCode(alias_code=outer, csi_code=None)
    if _COLORO_RE.match(outer) and _CSI_LIKE_RE.match(inner):
        return DualColorCode(alias_code=outer, csi_code=inner)
    if _CSI_LIKE_RE.match(inner) and not _CSI_LIKE_RE.match(outer):
        return DualColorCode(alias_code=outer, csi_code=inner)
    return DualColorCode(alias_code=outer, csi_code=None)


def apply_item_color_extract(row) -> None:
    """Isi color_code + color_qualifier dari teks color; jangan ubah color."""
    color = getattr(row, "color", None)
    row.color_code = extract_item_color_code(color)
    row.color_qualifier = extract_item_color_qualifier(color)


def csi_color_label(color_name: str | None, color_code: str | None) -> str:
    name = (color_name or "").strip()
    code = (color_code or "").strip()
    if name and code:
        if f"({code})".lower() in name.lower():
            return name
        return f"{name} ({code})"
    return name or code
