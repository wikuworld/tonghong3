"""Kode FG / SubKon berurutan, dan emboss master item dari color swatch."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import ColorSwatchRecipe, MasterItem
from app.services.color_code import extract_item_color_code


def item_code_series(category: str | None) -> tuple[str, int]:
    """PU dan Suede berbagi deret FG. SubKon punya deret SUB sendiri."""
    raw = str(category or "").strip().lower()
    if raw in {"subkon", "subcont", "subcontract"}:
        return "SUB", 4
    return "FG", 5


def next_code_from_existing(codes: list[str], prefix: str, width: int) -> str:
    number = 0
    for code in codes:
        raw = str(code or "").strip()
        if not raw.startswith(prefix):
            continue
        suffix = raw[len(prefix) :]
        if suffix.isdigit():
            number = max(number, int(suffix))
    nxt = number + 1
    pad = max(width, len(str(nxt)))
    return f"{prefix}{nxt:0{pad}d}"


def allocate_next_item_code(db: Session, category: str | None) -> str:
    prefix, width = item_code_series(category)
    codes = list(
        db.scalars(select(MasterItem.item_code).where(MasterItem.item_code.like(f"{prefix}%"))).all()
    )
    return next_code_from_existing([str(code or "") for code in codes], prefix, width)


def _unique_embosses(rows: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for raw in rows:
        emboss = " ".join(str(raw or "").split()).strip()
        key = emboss.casefold()
        if not emboss or key in seen:
            continue
        seen.add(key)
        out.append(emboss)
    out.sort(key=str.casefold)
    return out


def _swatch_emboss_query():
    return select(ColorSwatchRecipe.emboss).where(
        ColorSwatchRecipe.is_active.is_(True),
        func.trim(ColorSwatchRecipe.emboss) != "",
    )


def _collect_embosses(db: Session, stmt) -> list[str]:
    rows = list(db.scalars(stmt).all())
    return _unique_embosses([str(row or "") for row in rows])


def swatch_color_label(color_name: str | None, color_code: str | None) -> str:
    name = " ".join(str(color_name or "").split()).strip()
    code = " ".join(str(color_code or "").split()).strip()
    if name and code:
        return f"{name} ({code})"
    return name or code


def list_swatch_materials(db: Session) -> list[str]:
    rows = db.scalars(
        select(ColorSwatchRecipe.material_name).where(
            ColorSwatchRecipe.is_active.is_(True),
            func.trim(ColorSwatchRecipe.material_name) != "",
        )
    ).all()
    seen: set[str] = set()
    out: list[str] = []
    for raw in rows:
        name = " ".join(str(raw or "").split()).strip()
        key = name.casefold()
        if not name or key in seen:
            continue
        seen.add(key)
        out.append(name)
    out.sort(key=str.casefold)
    return out


def list_swatch_colors(db: Session, material_name: str | None) -> list[dict[str, str]]:
    material = " ".join(str(material_name or "").split()).strip()
    if not material:
        return []
    rows = db.execute(
        select(ColorSwatchRecipe.color_code, ColorSwatchRecipe.color_name).where(
            ColorSwatchRecipe.is_active.is_(True),
            func.lower(func.trim(ColorSwatchRecipe.material_name)) == material.lower(),
            func.trim(ColorSwatchRecipe.color_code) != "",
        )
    ).all()
    by_code: dict[str, str] = {}
    for code_raw, name_raw in rows:
        code = " ".join(str(code_raw or "").split()).strip().upper()
        name = " ".join(str(name_raw or "").split()).strip()
        if not code or code in by_code:
            continue
        by_code[code] = name
    colors = [
        {"label": swatch_color_label(name, code), "value": swatch_color_label(name, code)}
        for code, name in by_code.items()
    ]
    colors.sort(key=lambda row: row["label"].casefold())
    return colors


def list_swatch_embosses(
    db: Session,
    *,
    material_name: str | None,
    color: str | None = None,
) -> tuple[list[str], bool]:
    """Emboss hanya untuk pasangan material + kode warna yang sama di color swatch."""
    material = " ".join(str(material_name or "").split()).strip()
    code = extract_item_color_code(color)
    if not material or not code:
        return [], False
    found = _collect_embosses(
        db,
        _swatch_emboss_query().where(
            func.lower(func.trim(ColorSwatchRecipe.material_name)) == material.lower(),
            func.upper(func.trim(ColorSwatchRecipe.color_code)) == code,
        ),
    )
    return found, bool(found)
