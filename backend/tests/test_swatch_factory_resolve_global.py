"""Factory resolve harus mencakup varian pabrik (FENGTAY WEST, CHANGSHIN RJ, dll)."""

from sqlalchemy import select

from app.db import SessionLocal
from app.models import ColorSwatchRecipe, Customer
from app.services.color_swatch import resolve_swatch_factory_keys


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
        missing = []
        for fk in keys:
            if not fk:
                continue
            resolved = resolve_swatch_factory_keys(db, factory_hint=fk, customer_id=None)
            if fk not in resolved:
                missing.append(fk)
        assert not missing, f"factory_key tanpa resolve: {missing[:10]}"
    finally:
        db.close()
