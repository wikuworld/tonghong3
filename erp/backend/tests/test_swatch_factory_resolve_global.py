"""Factory resolve harus mencakup varian pabrik (FENGTAY WEST, CHANGSHIN RJ, dll)."""

import pytest
from sqlalchemy import select, text

from app.db import SessionLocal
from app.models import ColorSwatchRecipe, Customer
from app.services.color_swatch import resolve_swatch_factory_keys


def _db_available() -> bool:
    try:
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            return True
        finally:
            db.close()
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_available(), reason="MariaDB tidak tersedia (CI tanpa DB)")


def test_fengtay_west_includes_regional_variants():
    db = SessionLocal()
    try:
        c = db.scalar(select(Customer).where(Customer.code == "FT006"))
        assert c is not None
        keys = resolve_swatch_factory_keys(db, factory_hint=c.code, customer_id=c.id)
        assert "FENGTAY (WEST)" in keys or "FENGTAY WEST" in keys
        assert "FENGTAY" in keys
    finally:
        db.close()


def test_changshin_reksa_jaya_prefers_rj():
    db = SessionLocal()
    try:
        c = db.scalar(select(Customer).where(Customer.code == "CS005"))
        assert c is not None
        keys = resolve_swatch_factory_keys(db, factory_hint=c.code, customer_id=c.id)
        assert "CHANGSHIN RJ" in keys
    finally:
        db.close()


def test_all_swatch_factory_keys_resolvable_by_some_customer_or_hint():
    """Setiap factory_key aktif di swatch harus bisa di-resolve (hint = key itu sendiri)."""
    db = SessionLocal()
    try:
        keys = db.scalars(
            select(ColorSwatchRecipe.factory_key)
            .where(ColorSwatchRecipe.is_active.is_(True))
            .distinct()
        ).all()
        unresolved = []
        for key in keys:
            resolved = resolve_swatch_factory_keys(db, factory_hint=key, customer_id=None)
            if key not in resolved and not resolved:
                unresolved.append(key)
        assert not unresolved, f"factory_key tidak resolve: {unresolved[:20]}"
    finally:
        db.close()
