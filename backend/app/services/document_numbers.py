"""Penyesuaian inisial nomor Surat Jalan (THI-…) dan Invoice (IN-…) berdasarkan kategori PO."""

from __future__ import annotations

import re

from app.models import PoHeader

# Huruf tengah setelah THI- / IN- selaras permintaan marketing (prod / sample / klaim / retur / subkon / suede / sample FOC).
_CATEGORY_LETTER: dict[str, str] = {
    "production": "C",
    "sample": "M",
    "claim": "L",
    "return": "R",
    "subcont": "K",
    "suede": "D",
}


def category_letter_for_po(ph: PoHeader | None) -> str:
    if not ph:
        return "C"
    ol = (ph.order_type_label or "").upper()
    if "FOC" in ol:
        return "F"
    c = (ph.po_category or "production").lower()
    return _CATEGORY_LETTER.get(c, "C")


def _swap_middle_letter(stored: str, letter: str, prefix: str) -> str:
    s = (stored or "").strip()
    if not s:
        return ""
    pfx = prefix.upper()
    m = re.match(rf"^({re.escape(pfx)})-([A-Za-z])(.+)$", s, re.IGNORECASE)
    if m:
        return f"{m.group(1).upper()}-{letter.upper()}{m.group(3)}"
    return s


def surat_jalan_display_number(stored: str, ph: PoHeader | None) -> str:
    return _swap_middle_letter(stored, category_letter_for_po(ph), "THI")


def invoice_display_number(stored: str, ph: PoHeader | None) -> str:
    return _swap_middle_letter(stored, category_letter_for_po(ph), "IN")
