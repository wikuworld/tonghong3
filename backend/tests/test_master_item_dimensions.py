"""Unit: kombinasi material + ketebalan + warna untuk master item."""

from decimal import Decimal

from app.models import MasterItem
from app.services.master_item_dimensions import (
    distinct_colors,
    distinct_material_names,
    distinct_thicknesses,
    resolve_by_dimensions,
)


def _mi(**kw) -> MasterItem:
    """Minimal ORM-like object (tanpa DB)."""
    defaults: dict = {
        "id": 0,
        "item_code": "",
        "thickness_mm": None,
        "thickness_range": None,
        "material_name": None,
        "emboss": None,
        "color": None,
        "softness": None,
        "color_reference": None,
        "color_standard": None,
        "model_takedown": None,
        "backing": None,
        "quantity_order_default": None,
        "style_article": None,
        "model": None,
        "category": None,
        "exim_material_code": None,
    }
    defaults.update(kw)
    return MasterItem(**defaults)


def test_distinct_materials_and_cascade() -> None:
    rows = [
        _mi(id=1, item_code="A1", material_name="PU X", thickness_range="1.2-1.4", color="Black"),
        _mi(id=2, item_code="A2", material_name="PU X", thickness_range="1.2-1.4", color="White"),
        _mi(id=3, item_code="B1", material_name="SUEDE Y", thickness_range="1.4-1.6", color="Navy"),
    ]
    assert distinct_material_names(rows) == ["PU X", "SUEDE Y"]
    assert distinct_thicknesses(rows, "PU X") == ["1.2 - 1.4"]
    assert set(distinct_colors(rows, "PU X", "1.2 - 1.4")) == {"Black", "White"}


def test_resolve_single_and_ambiguous() -> None:
    rows = [
        _mi(id=1, item_code="A1", material_name="PU X", thickness_range="1.2-1.4", color="Black"),
        _mi(id=2, item_code="A2", material_name="PU X", thickness_range="1.2-1.4", color="White"),
    ]
    black = resolve_by_dimensions(rows, material_name="PU X", thickness_text="1.2 - 1.4", color="Black")
    assert len(black) == 1 and black[0].id == 1
    white = resolve_by_dimensions(rows, material_name="PU X", thickness_text="1.2-1.4", color="white")
    assert len(white) == 1 and white[0].id == 2


def test_thickness_mm_fallback() -> None:
    rows = [
        _mi(id=1, item_code="Z1", material_name="M", thickness_range="", thickness_mm=Decimal("1.5"), color="Red"),
    ]
    assert distinct_thicknesses(rows, "M") == ["1.4 - 1.6"]
    hits = resolve_by_dimensions(rows, material_name="M", thickness_text="1.4 - 1.6", color="Red")
    assert len(hits) == 1
