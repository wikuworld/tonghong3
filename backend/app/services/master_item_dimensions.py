"""Kombinasi material + ketebalan + warna untuk cascade UI dan resolve ke MasterItem."""

from __future__ import annotations

from app.models import MasterItem
from app.services.thickness_format import (
    canonical_thickness_range,
    display_thickness_range,
    thickness_ranges_equivalent,
)


def _norm_text(value: str | None) -> str:
    return " ".join(str(value or "").strip().lower().split())


_CATEGORY_ALIASES = {
    "pu": "pu",
    "suide": "suide",
    "suede": "suide",
    "subkon": "subkon",
    "subcont": "subkon",
    "subcontract": "subkon",
}


def filter_by_category(rows: list[MasterItem], category: str | None) -> list[MasterItem]:
    raw = (category or "").strip().lower()
    if not raw:
        return rows
    target = _CATEGORY_ALIASES.get(raw, raw)
    out: list[MasterItem] = []
    for row in rows:
        cat = (row.category or "").strip().lower()
        norm = _CATEGORY_ALIASES.get(cat, cat)
        if norm == target:
            out.append(row)
    return out


def master_item_thickness_display(row: MasterItem) -> str:
    if row.thickness_range and str(row.thickness_range).strip():
        return canonical_thickness_range(str(row.thickness_range).strip())
    if row.thickness_mm is not None:
        return canonical_thickness_range(str(row.thickness_mm).strip())
    return ""


def thickness_matches(row: MasterItem, thickness_text: str | None) -> bool:
    u = (thickness_text or "").strip()
    if not u:
        return False
    disp = master_item_thickness_display(row)
    if not disp:
        return False
    return thickness_ranges_equivalent(disp, u)


def filter_by_material(rows: list[MasterItem], material_name: str) -> list[MasterItem]:
    m = _norm_text(material_name)
    return [r for r in rows if _norm_text(r.material_name or "") == m]


def distinct_material_names(rows: list[MasterItem]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for r in rows:
        v = (r.material_name or "").strip()
        if not v:
            continue
        key = _norm_text(v)
        if key in seen:
            continue
        seen.add(key)
        out.append(v)
    return sorted(out, key=lambda s: s.lower())


def distinct_thicknesses(rows: list[MasterItem], material_name: str) -> list[str]:
    fr = filter_by_material(rows, material_name)
    seen: set[str] = set()
    out: list[str] = []
    for r in fr:
        d = master_item_thickness_display(r)
        if not d:
            continue
        k = _norm_text(d)
        if k in seen:
            continue
        seen.add(k)
        out.append(display_thickness_range(d))
    return sorted(out, key=lambda s: s.lower())


def distinct_colors(rows: list[MasterItem], material_name: str, thickness_text: str | None) -> list[str]:
    fr = filter_by_material(rows, material_name)
    if thickness_text and str(thickness_text).strip():
        fr = [r for r in fr if thickness_matches(r, thickness_text)]
    else:
        return []
    seen: set[str] = set()
    out: list[str] = []
    for r in fr:
        c = (r.color or "").strip()
        if not c:
            continue
        k = _norm_text(c)
        if k in seen:
            continue
        seen.add(k)
        out.append(c)
    return sorted(out, key=lambda s: s.lower())


def emboss_display(row: MasterItem) -> str:
    v = (row.emboss or "").strip()
    return v if v else "-"


def emboss_matches(row: MasterItem, emboss: str | None) -> bool:
    raw = (emboss or "").strip()
    if not raw:
        return True
    e = _norm_text(raw)
    row_e = _norm_text(row.emboss or "")
    if e in ("", "-"):
        return row_e in ("", "-")
    return row_e == e


def _filter_by_color(rows: list[MasterItem], color: str | None) -> list[MasterItem]:
    c = _norm_text(color)
    if not c:
        return []
    return [r for r in rows if _norm_text(r.color or "") == c]


def distinct_embosses(
    rows: list[MasterItem],
    material_name: str,
    thickness_text: str | None,
    color: str | None,
) -> list[str]:
    fr = filter_by_material(rows, material_name)
    if thickness_text and str(thickness_text).strip():
        fr = [r for r in fr if thickness_matches(r, thickness_text)]
    else:
        return []
    fr = _filter_by_color(fr, color)
    seen: set[str] = set()
    out: list[str] = []
    for r in fr:
        v = emboss_display(r)
        k = _norm_text(v)
        if k in seen:
            continue
        seen.add(k)
        out.append(v)
    return sorted(out, key=lambda s: s.lower())


def distinct_item_codes(
    rows: list[MasterItem],
    material_name: str,
    thickness_text: str | None,
    color: str | None,
    emboss: str | None = None,
) -> list[str]:
    fr = filter_by_material(rows, material_name)
    if thickness_text and str(thickness_text).strip():
        fr = [r for r in fr if thickness_matches(r, thickness_text)]
    else:
        return []
    fr = _filter_by_color(fr, color)
    if emboss and str(emboss).strip():
        fr = [r for r in fr if emboss_matches(r, emboss)]
    seen: set[str] = set()
    out: list[str] = []
    for r in fr:
        code = (r.item_code or "").strip()
        if not code:
            continue
        k = code.upper()
        if k in seen:
            continue
        seen.add(k)
        out.append(code)
    return sorted(out, key=str.upper)


def resolve_by_dimensions(
    rows: list[MasterItem],
    *,
    material_name: str,
    thickness_text: str,
    color: str,
    emboss: str | None = None,
) -> list[MasterItem]:
    fr = filter_by_material(rows, material_name)
    fr = [r for r in fr if thickness_matches(r, thickness_text)]
    c = _norm_text(color)
    fr = [r for r in fr if _norm_text(r.color or "") == c]
    if emboss and str(emboss).strip():
        fr = [r for r in fr if emboss_matches(r, emboss)]
    return fr
