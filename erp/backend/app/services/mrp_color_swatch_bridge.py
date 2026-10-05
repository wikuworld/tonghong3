"""Map color_swatch_recipes → opsi & kombinasi MRP rencana produksi."""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ColorSwatchRecipe, MasterItem
from app.services.color_code import csi_color_label
from app.services.color_swatch import filter_swatch_recipes_by_dimensions
from app.services.master_item_dimensions import master_item_thickness_display, thickness_matches
from app.services.mrp_master_item_bridge import _distinct, _norm, item_to_erp_row
from app.services.thickness_format import display_thickness_range


def _recipe_color_label(recipe: ColorSwatchRecipe) -> str:
    name = (recipe.color_name or "").strip()
    if getattr(recipe, "csi_color_master_id", None):
        return csi_color_label(name, recipe.color_code)
    return name


def load_swatch_recipes(db: Session) -> list[ColorSwatchRecipe]:
    return list(
        db.scalars(
            select(ColorSwatchRecipe)
            .where(ColorSwatchRecipe.is_active.is_(True))
            .order_by(
                ColorSwatchRecipe.material_name.asc(),
                ColorSwatchRecipe.emboss.asc(),
                ColorSwatchRecipe.color_name.asc(),
            )
        ).all()
    )


def _combo_key(material: str, emboss: str) -> str:
    return f"{_norm(material)}\x1e{_norm(emboss)}"


def options_for_rencana(
    db: Session,
    recipes: list[ColorSwatchRecipe],
    master_items: list[MasterItem],
) -> dict[str, Any]:
    materials: list[str] = []
    embosses_by_material: dict[str, list[str]] = {}
    colors_by_material_emboss: dict[str, list[str]] = {}
    color_labels: dict[str, str] = {}

    for recipe in recipes:
        mat = (recipe.material_name or "").strip()
        emb = (recipe.emboss or "").strip()
        col = (recipe.color_name or "").strip()
        if not mat:
            continue
        materials.append(mat)
        if emb:
            embosses_by_material.setdefault(mat, []).append(emb)
        if emb and col:
            colors_by_material_emboss.setdefault(_combo_key(mat, emb), []).append(col)
            if col not in color_labels or getattr(recipe, "csi_color_master_id", None):
                color_labels[col] = _recipe_color_label(recipe)

    return {
        "thickness": _distinct(
            [
                display_thickness_range(master_item_thickness_display(r))
                for r in master_items
                if master_item_thickness_display(r)
            ]
        ),
        "materials": _distinct(materials),
        "colors": [],
        "emboss": [],
        "embosses_by_material": {
            mat: _distinct(vals) for mat, vals in sorted(embosses_by_material.items())
        },
        "colors_by_material_emboss": {
            key: _distinct(vals) for key, vals in sorted(colors_by_material_emboss.items())
        },
        "color_labels": color_labels,
        "customers": [],
        "color_swatch": _distinct([(r.factory_key or "") for r in recipes if r.factory_key]),
        "categories": [],
        "source": "color_swatch_recipes",
    }


def fields_from_swatch(
    db: Session,
    recipes: list[ColorSwatchRecipe],
    master_items: list[MasterItem],
    *,
    thickness: str = "",
    material_name: str = "",
    color: str = "",
) -> dict[str, Any]:
    filtered_recipes = recipes
    if material_name.strip():
        filtered_recipes = filter_swatch_recipes_by_dimensions(
            filtered_recipes,
            material_name=material_name,
            db=db,
        )
    if color.strip():
        filtered_recipes = filter_swatch_recipes_by_dimensions(
            filtered_recipes,
            color_name=color,
            db=db,
        )

    embosses = _distinct([(r.emboss or "") for r in filtered_recipes])
    colors = _distinct([(r.color_name or "") for r in filtered_recipes])
    materials = _distinct([(r.material_name or "") for r in filtered_recipes])

    return {
        "thicknesses": _distinct(
            [
                display_thickness_range(master_item_thickness_display(r))
                for r in master_items
                if master_item_thickness_display(r)
            ]
        ),
        "material_names": materials,
        "colors": colors,
        "embosses": embosses,
        "customers": [],
        "source": "color_swatch_recipes",
    }


def _recipe_to_combo_row(recipe: ColorSwatchRecipe) -> dict[str, Any]:
    return {
        "id": int(recipe.id),
        "color_swatch": (recipe.factory_key or "").strip(),
        "factory_key": (recipe.factory_key or "").strip(),
        "backer": (recipe.backing or "").strip() or None,
        "material_name": recipe.material_name,
        "color": recipe.color_name,
        "emboss": recipe.emboss,
        "buyer_code": recipe.buyer_code,
        "color_code": recipe.color_code,
        "csi_color_master_id": getattr(recipe, "csi_color_master_id", None),
        "source": "color_swatch_recipes",
    }


def combination_from_swatch(
    db: Session,
    recipes: list[ColorSwatchRecipe],
    master_items: list[MasterItem],
    *,
    material_name: str,
    color: str,
    emboss: str,
    thickness: str = "",
    color_code: str = "",
) -> list[dict[str, Any]]:
    from app.services.mrp_master_item_bridge import combination_from_items, resolve_backer

    hits = filter_swatch_recipes_by_dimensions(
        recipes,
        material_name=material_name,
        color_name=color,
        emboss=emboss,
        db=db,
    )
    if color_code.strip():
        code = color_code.strip().upper()
        coded = [r for r in hits if (r.color_code or "").strip().upper() == code]
        if coded:
            hits = coded
    hits = sorted(
        hits,
        key=lambda r: (0 if getattr(r, "csi_color_master_id", None) else 1, int(getattr(r, "id", 0) or 0)),
    )

    out: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for recipe in hits:
        sw = (recipe.factory_key or "").strip()
        backer = (recipe.backing or "").strip()
        key = (_norm(sw), _norm(backer), _norm(recipe.buyer_code))
        if key in seen:
            continue
        seen.add(key)
        row = _recipe_to_combo_row(recipe)
        if thickness.strip():
            item_hits = [
                r
                for r in master_items
                if _norm(r.material_name) == _norm(material_name)
                and _norm(r.color) == _norm(color)
                and _norm(r.emboss) == _norm(emboss)
                and thickness_matches(r, thickness)
            ]
            if item_hits:
                mapped = item_to_erp_row(item_hits[0])
                row["thickness"] = mapped.get("thickness")
                if not row.get("backer") and mapped.get("backer"):
                    row["backer"] = mapped.get("backer")
        if not row.get("backer"):
            resolved = resolve_backer(
                master_items,
                material_name=material_name,
                thickness=thickness or "",
                color=color,
                emboss=emboss,
            )
            if resolved:
                row["backer"] = resolved
        out.append(row)

    if out:
        return out

    # Fallback: spek SO tidak ketemu di color swatch → pakai Master Item (backing).
    return combination_from_items(
        master_items,
        material_name=material_name,
        color=color,
        emboss=emboss,
        thickness=thickness,
    )

def resolve_backer_from_swatch(
    db: Session,
    recipes: list[ColorSwatchRecipe],
    *,
    material_name: str,
    color: str,
    emboss: str,
    color_swatch: str | None = None,
) -> Optional[str]:
    hits = filter_swatch_recipes_by_dimensions(
        recipes,
        material_name=material_name,
        color_name=color,
        emboss=emboss,
        db=db,
    )
    if color_swatch and str(color_swatch).strip():
        sw = _norm(color_swatch)
        hits = [r for r in hits if _norm(r.factory_key) == sw]
    for recipe in hits:
        backer = (recipe.backing or "").strip()
        if backer:
            return backer
    return None
