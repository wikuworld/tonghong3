"""Tolerant spek matching for MRP master PO (parity dengan ERP color_swatch)."""

from __future__ import annotations

import re
from typing import Any

_PAREN_SUFFIX_RE = re.compile(r"\s*\([^)]*\)\s*$")
_EMBOSS_CODE_RE = re.compile(r"^([A-Z]{1,4}-\d+[A-Z]?)", re.IGNORECASE)
_THICKNESS_RANGE_RE = re.compile(r"^\s*([\d.]+)\s*[-–]\s*([\d.]+)\s*$")


def _norm(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _canonical_thickness(text: Any) -> str:
    raw = str(text or "").strip().replace("mm", "").strip()
    if not raw or raw in {"-", "—", "–"}:
        return ""
    m = _THICKNESS_RANGE_RE.match(raw)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    return raw


def thickness_matches(row_thickness: Any, want: Any) -> bool:
    a = _canonical_thickness(row_thickness)
    b = _canonical_thickness(want)
    if not a or not b:
        return False
    return _norm(a) == _norm(b) or a.replace(" ", "") == b.replace(" ", "")


def _parse_thickness_point(text: Any) -> float | None:
    raw = str(text or "").strip().replace("mm", "").strip()
    if not raw or raw in {"-", "—", "–"} or _THICKNESS_RANGE_RE.match(raw):
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def thickness_point_in_range(point: Any, spec: Any) -> bool:
    """Tebal titik (1.2) lolos bila masuk rentang order (1.2 - 1.4), atau keduanya sama."""
    if thickness_matches(point, spec):
        return True
    val = _parse_thickness_point(point)
    raw_spec = str(spec or "").strip().replace("mm", "").strip()
    match = _THICKNESS_RANGE_RE.match(raw_spec)
    if val is None or not match:
        return False
    lo = float(match.group(1))
    hi = float(match.group(2))
    if lo > hi:
        lo, hi = hi, lo
    return lo - 1e-9 <= val <= hi + 1e-9


def yl_spek_reject_reason(
    *,
    yl_warna: Any,
    yl_tebal: Any,
    rencana_warna: Any,
    rencana_tebal: Any,
    require_color_match: bool = True,
) -> str | None:
    """None bila YL boleh discan. String alasan bila spek tidak cocok.

    Persiapan kulit (proses): require_color_match=False — hanya tebal vs rencana/SO.
    """
    if require_color_match:
        warna = str(yl_warna or "").strip()
        if not warna:
            return "Warna YL kosong, tidak dapat dipakai pada rencana ini."
        if not swatch_colors_match(warna, rencana_warna):
            rencana = str(rencana_warna or "").strip() or "-"
            return f"Warna YL ({warna}) tidak cocok dengan warna rencana ({rencana})."
    tebal = str(yl_tebal or "").strip()
    if not tebal:
        return "Tebal YL kosong, tidak dapat dipakai pada rencana ini."
    if not thickness_point_in_range(tebal, rencana_tebal):
        rencana_t = str(rencana_tebal or "").strip() or "-"
        return f"Tebal YL ({tebal}) di luar spek rencana ({rencana_t})."
    return None


def normalize_swatch_color_name(text: str | None) -> str:
    s = re.sub(r"\s+", " ", (text or "").strip())
    s = _PAREN_SUFFIX_RE.sub("", s).strip()
    return s.lower()


def swatch_colors_match(a: str | None, b: str | None) -> bool:
    na = normalize_swatch_color_name(a)
    nb = normalize_swatch_color_name(b)
    if not na or not nb:
        return False
    return na == nb or na.startswith(nb) or nb.startswith(na)


def _extract_emboss_code_token(token: str) -> str | None:
    raw = (token or "").strip().upper()
    if not raw:
        return None
    m = _EMBOSS_CODE_RE.match(raw)
    if m:
        return m.group(1).upper()
    compact = re.sub(r"\s+", "", raw)
    m2 = _EMBOSS_CODE_RE.match(compact)
    return m2.group(1).upper() if m2 else None


def swatch_emboss_code(text: str | None) -> str:
    s = re.sub(r"\s+", " ", (text or "").strip())
    s = _PAREN_SUFFIX_RE.sub("", s).strip()
    if not s:
        return ""
    for token in s.split():
        code = _extract_emboss_code_token(token)
        if code:
            return code
    code = _extract_emboss_code_token(s)
    return code or s.split()[0].upper()


def swatch_emboss_match(a: str | None, b: str | None) -> bool:
    ca = swatch_emboss_code(a)
    cb = swatch_emboss_code(b)
    if not ca or not cb:
        return False
    if ca == cb:
        return True
    return ca.startswith(cb) or cb.startswith(ca)


def material_matches(po_item_name: Any, want_material: Any) -> bool:
    a = _norm(po_item_name)
    b = _norm(want_material)
    if not a or not b:
        return False
    if a == b:
        return True
    return a.startswith(b) or b.startswith(a)


def po_matches_spek(
    po: dict[str, Any],
    *,
    material_name: str = "",
    thickness: str = "",
    color: str = "",
    emboss: str = "",
    color_swatch: str = "",
) -> bool:
    if material_name.strip() and not material_matches(po.get("item_name"), material_name):
        return False
    if thickness.strip() and not thickness_matches(po.get("tebal"), thickness):
        return False
    if color.strip() and not swatch_colors_match(po.get("warna"), color):
        return False
    if emboss.strip() and not swatch_emboss_match(po.get("emboss"), emboss):
        return False
    if color_swatch.strip():
        sw = (po.get("color_swatch") or "").strip()
        if _norm(sw) != _norm(color_swatch):
            return False
    return True


def filter_master_po_by_spek(
    items: list[dict[str, Any]],
    *,
    material_name: str = "",
    thickness: str = "",
    color: str = "",
    emboss: str = "",
    color_swatch: str = "",
) -> list[dict[str, Any]]:
    return [
        row
        for row in items
        if po_matches_spek(
            row,
            material_name=material_name,
            thickness=thickness,
            color=color,
            emboss=emboss,
            color_swatch=color_swatch,
        )
    ]
