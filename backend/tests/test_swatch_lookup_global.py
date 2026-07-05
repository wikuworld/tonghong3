"""Lookup swatch harus berfungsi untuk seluruh resep aktif (bukan satu customer/material saja)."""

from sqlalchemy import select

from app.db import SessionLocal
from app.models import ColorSwatchRecipe
from app.services.color_swatch import (
    filter_swatch_recipes_by_dimensions,
    resolve_swatch_factory_keys,
)


def test_every_active_recipe_matches_with_master_style_suffixes():
    db = SessionLocal()
    try:
        recipes = list(
            db.scalars(
                select(ColorSwatchRecipe).where(ColorSwatchRecipe.is_active.is_(True))
            ).all()
        )
        failures: list[int] = []
        for recipe in recipes:
            factory_keys = resolve_swatch_factory_keys(
                db, factory_hint=recipe.factory_key, customer_id=None
            )
            pool = [
                row
                for row in recipes
                if row.buyer_code == recipe.buyer_code
                and row.factory_key in factory_keys
            ]
            matched = filter_swatch_recipes_by_dimensions(
                pool,
                material_name=recipe.material_name,
                color_name=f"{recipe.color_name} (TST)" if recipe.color_name else None,
                emboss=f"{recipe.emboss} (MATTE)" if recipe.emboss else None,
            )
            if not any(row.id == recipe.id for row in matched):
                failures.append(recipe.id)
        assert not failures, f"resep gagal match: {failures[:20]}"
    finally:
        db.close()
