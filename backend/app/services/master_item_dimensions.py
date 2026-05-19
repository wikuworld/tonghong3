"""Kombinasi material + ketebalan + warna untuk cascade UI dan resolve ke MasterItem."""

from __future__ import annotations

from app.models import MasterItem


def _norm_text(value: str | None) -> str:
    return " ".join(str(value or "").strip().lower().split())


def master_item_thickness_display(row: MasterItem) -> str:
    if row.thickness_range and str(row.thickness_range).strip():
        return str(row.thickness_range).strip()
    if row.thickness_mm is not None:
        return str(row.thickness_mm).strip()
    return ""


def thickness_matches(row: MasterItem, thickness_text: str | None) -> bool:
    u = (thickness_text or "").strip()
    if not u:
        return False
    disp = master_item_thickness_display(row)
    if not disp:
        return False
    if _norm_text(disp) == _norm_text(u):
        return True
    return disp.replace(" ", "") == u.replace(" ", "")


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
        out.append(d)
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


def resolve_by_dimensions(
    rows: list[MasterItem],
    *,
    material_name: str,
    thickness_text: str,
    color: str,
) -> list[MasterItem]:
    fr = filter_by_material(rows, material_name)
    fr = [r for r in fr if thickness_matches(r, thickness_text)]
    c = _norm_text(color)
    return [r for r in fr if _norm_text(r.color or "") == c]
