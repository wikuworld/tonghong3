"""Map Master Item ERP → bentuk respons MRP (master_erp / options / combination)."""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MasterItem
from app.services.master_item_dimensions import (
    master_item_thickness_display,
    resolve_by_dimensions,
    thickness_matches,
)
from app.services.thickness_format import display_thickness_range


def _norm(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _distinct(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for raw in values:
        v = (raw or "").strip()
        if not v:
            continue
        key = _norm(v)
        if key in seen:
            continue
        seen.add(key)
        out.append(v)
    return sorted(out, key=lambda s: s.lower())


def load_master_items(db: Session) -> list[MasterItem]:
    return list(db.scalars(select(MasterItem).order_by(MasterItem.item_code)).all())


def item_to_erp_row(row: MasterItem) -> dict[str, Any]:
    thickness = master_item_thickness_display(row)
    return {
        "id": int(row.id),
        "erp_master_item_id": int(row.id),
        "item_code": row.item_code,
        "category": row.category,
        "thickness": display_thickness_range(thickness) if thickness else None,
        "material_name": row.material_name,
        "color": row.color,
        "emboss": row.emboss,
        "color_swatch": row.color_reference or row.color_standard,
        "backer": row.backing,
        "customer": None,
        "source": "master_items",
    }


def list_erp_rows(db: Session, *, limit: int = 500, keyword: str | None = None) -> list[dict[str, Any]]:
    rows = load_master_items(db)
    q = _norm(keyword)
    out: list[dict[str, Any]] = []
    for row in rows:
        mapped = item_to_erp_row(row)
        if q:
            blob = " ".join(
                str(mapped.get(k) or "")
                for k in (
                    "item_code",
                    "category",
                    "thickness",
                    "material_name",
                    "color",
                    "emboss",
                    "color_swatch",
                    "backer",
                )
            )
            if q not in _norm(blob):
                continue
        out.append(mapped)
        if len(out) >= limit:
            break
    return out


def options_from_items(rows: list[MasterItem]) -> dict[str, Any]:
    return {
        "thickness": _distinct(
            [
                display_thickness_range(master_item_thickness_display(r))
                for r in rows
                if master_item_thickness_display(r)
            ]
        ),
        "materials": _distinct([(r.material_name or "") for r in rows]),
        "colors": _distinct([(r.color or "") for r in rows]),
        "emboss": _distinct([(r.emboss or "") for r in rows]),
        "customers": [],
        "color_swatch": _distinct(
            [(r.color_reference or r.color_standard or "") for r in rows]
        ),
        "categories": _distinct([(r.category or "") for r in rows]),
        "source": "master_items",
    }


def fields_from_items(
    rows: list[MasterItem],
    *,
    thickness: str = "",
    material_name: str = "",
    color: str = "",
) -> dict[str, Any]:
    filtered = rows
    if thickness.strip():
        filtered = [r for r in filtered if thickness_matches(r, thickness)]
    if material_name.strip():
        m = _norm(material_name)
        filtered = [r for r in filtered if _norm(r.material_name) == m]
    if color.strip():
        c = _norm(color)
        filtered = [r for r in filtered if _norm(r.color) == c]

    return {
        "thicknesses": _distinct(
            [
                display_thickness_range(master_item_thickness_display(r))
                for r in rows
                if master_item_thickness_display(r)
            ]
        ),
        "material_names": _distinct([(r.material_name or "") for r in filtered]),
        "colors": _distinct([(r.color or "") for r in filtered]),
        "embosses": _distinct([(r.emboss or "") for r in filtered]),
        "customers": [],
        "source": "master_items",
    }


def combination_from_items(
    rows: list[MasterItem],
    *,
    material_name: str,
    color: str,
    emboss: str,
    thickness: str = "",
) -> list[dict[str, Any]]:
    m, c, e = _norm(material_name), _norm(color), _norm(emboss)
    hits: list[MasterItem] = []
    for r in rows:
        if _norm(r.material_name) != m:
            continue
        if _norm(r.color) != c:
            continue
        if _norm(r.emboss) != e:
            continue
        if thickness.strip() and not thickness_matches(r, thickness):
            continue
        hits.append(r)
    return [item_to_erp_row(r) for r in hits]


def resolve_backer(
    rows: list[MasterItem],
    *,
    material_name: str,
    thickness: str,
    color: str,
    emboss: str | None = None,
) -> Optional[str]:
    hits = resolve_by_dimensions(
        rows,
        material_name=material_name,
        thickness_text=thickness,
        color=color,
    )
    if emboss and str(emboss).strip() and str(emboss).strip() != "-":
        e = _norm(emboss)
        narrowed = [r for r in hits if _norm(r.emboss) == e]
        if narrowed:
            hits = narrowed
    for r in hits:
        if r.backing and str(r.backing).strip():
            return str(r.backing).strip()
    return None
