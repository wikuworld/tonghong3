"""Tests import_recipes replace_inactive behaviour."""

from datetime import datetime
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from openpyxl import Workbook

from app.services.color_swatch import import_recipes, iter_upload_recipes


def _recipe(**kwargs):
    defaults = {
        "factory_key": "NIKOMAS",
        "buyer_code": "ADIDAS",
        "color_code": "A1",
        "color_name": "RED",
        "emboss": "DE-7",
        "material_name": "PU COATED",
        "is_active": True,
        "updated_at": None,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_import_recipes_replace_inactive_pair_scope():
    stale = _recipe(color_code="OLD", color_name="OLD RED")
    active = _recipe(color_code="A1", color_name="RED")
    other_factory = _recipe(
        factory_key="FENGTAY",
        color_code="Z9",
        color_name="KEEP",
    )

    db = MagicMock()
    call_count = {"n": 0}

    def _scalars(_stmt):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return MagicMock(first=lambda: None)
        if call_count["n"] == 2:
            return MagicMock(all=lambda: [active, stale])
        return MagicMock(first=lambda: None, all=lambda: [])

    db.scalars.side_effect = _scalars

    recipes = [
        {
            "factory_key": "NIKOMAS",
            "buyer_code": "ADIDAS",
            "color_code": "A1",
            "color_name": "RED",
            "emboss": "DE-7",
            "material_name": "PU COATED",
        }
    ]

    with patch("app.services.color_swatch._resolve_customer_id", return_value=None), patch(
        "app.services.color_swatch._resolve_brand_id", return_value=None
    ), patch(
        "app.services.buyer_registry.collect_unknown_buyer_codes", return_value=[]
    ), patch(
        "app.services.material_aliases.material_missing_in_master_items", return_value=False
    ):
        stats = import_recipes(
            db, recipes, replace_inactive=True, replace_inactive_scope="pair"
        )

    assert stats["deactivated"] == 1
    assert stale.is_active is False
    assert active.is_active is True
    assert other_factory.is_active is True
    assert isinstance(stale.updated_at, datetime)
    db.commit.assert_called()


def test_import_recipes_replace_inactive_global_scope():
    stale_same = _recipe(color_code="OLD", color_name="OLD RED")
    active = _recipe(color_code="A1", color_name="RED")
    other_factory = _recipe(
        factory_key="FENGTAY",
        color_code="Z9",
        color_name="OTHER",
    )

    db = MagicMock()
    call_count = {"n": 0}

    def _scalars(_stmt):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return MagicMock(first=lambda: None)
        if call_count["n"] == 2:
            return MagicMock(all=lambda: [active, stale_same, other_factory])
        return MagicMock(first=lambda: None, all=lambda: [])

    db.scalars.side_effect = _scalars

    recipes = [
        {
            "factory_key": "NIKOMAS",
            "buyer_code": "ADIDAS",
            "color_code": "A1",
            "color_name": "RED",
            "emboss": "DE-7",
            "material_name": "PU COATED",
        }
    ]

    with patch("app.services.color_swatch._resolve_customer_id", return_value=None), patch(
        "app.services.color_swatch._resolve_brand_id", return_value=None
    ), patch(
        "app.services.buyer_registry.collect_unknown_buyer_codes", return_value=[]
    ), patch(
        "app.services.material_aliases.material_missing_in_master_items", return_value=False
    ):
        stats = import_recipes(
            db, recipes, replace_inactive=True, replace_inactive_scope="global"
        )

    assert stats["deactivated"] == 2
    assert stale_same.is_active is False
    assert other_factory.is_active is False
    assert active.is_active is True
    db.commit.assert_called()


def test_import_recipes_replace_inactive_deactivates_missing():
    """Backward-compat alias: default scope is global when replace_inactive=True. """
    stale = _recipe(color_code="OLD", color_name="OLD RED")
    active = _recipe(color_code="A1", color_name="RED")

    db = MagicMock()
    call_count = {"n": 0}

    def _scalars(_stmt):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return MagicMock(first=lambda: None)
        if call_count["n"] == 2:
            return MagicMock(all=lambda: [active, stale])
        return MagicMock(first=lambda: None, all=lambda: [])

    db.scalars.side_effect = _scalars

    recipes = [
        {
            "factory_key": "NIKOMAS",
            "buyer_code": "ADIDAS",
            "color_code": "A1",
            "color_name": "RED",
            "emboss": "DE-7",
            "material_name": "PU COATED",
        }
    ]

    with patch("app.services.color_swatch._resolve_customer_id", return_value=None), patch(
        "app.services.color_swatch._resolve_brand_id", return_value=None
    ), patch(
        "app.services.buyer_registry.collect_unknown_buyer_codes", return_value=[]
    ), patch(
        "app.services.material_aliases.material_missing_in_master_items", return_value=False
    ):
        stats = import_recipes(db, recipes, replace_inactive=True)

    assert stats["deactivated"] == 1
    assert stale.is_active is False
    assert active.is_active is True
    db.commit.assert_called()


def test_import_recipes_without_replace_keeps_missing_active():
    stale = _recipe(color_code="OLD", color_name="OLD RED")
    db = MagicMock()
    db.scalars.side_effect = lambda _stmt: MagicMock(first=lambda: None, all=lambda: [stale])
    recipes = [
        {
            "factory_key": "NIKOMAS",
            "buyer_code": "ADIDAS",
            "color_code": "A1",
            "color_name": "RED",
            "emboss": "DE-7",
            "material_name": "PU COATED",
            "color_standard": "TSBI0202024010101",
        }
    ]
    with patch("app.services.color_swatch._resolve_customer_id", return_value=None), patch(
        "app.services.color_swatch._resolve_brand_id", return_value=None
    ), patch(
        "app.services.buyer_registry.collect_unknown_buyer_codes", return_value=[]
    ), patch(
        "app.services.material_aliases.material_missing_in_master_items", return_value=False
    ):
        stats = import_recipes(db, recipes, replace_inactive=False)
    assert stats["deactivated"] == 0
    assert stale.is_active is True


def _sample_rows():
    return [
        ["CUSTOMER", "BRAND", "COLOR CODE", "COLOR NAME", "EMBOS", "COLOR SWATCH", "BACKING", "MATERIAL", "NO URUT", "TGGL MASUK"],
        ["NIKOMAS", "NIKE", "A1", "RED", "DE-7", "TSBI0202024010101", "SF", "PU COATED", "1", "22/Jan/26"],
        ["NIKOMAS", "NIKE", "B2", "BLUE", "DE-7", "FOLLOW COLORO", "", "PU COATED", "2", ""],
        ["NIKOMAS", "NIKE", "C3", "GREEN", "DE-7", "", "", "PU COATED", "3", ""],
    ]


def test_upload_csv_keeps_color_standard_text():
    lines = [";".join(row) for row in _sample_rows()]
    raw = "\n".join(lines).encode("utf-8")
    parsed = iter_upload_recipes(raw, "swatch.csv")
    by_code = {row["color_code"]: row["color_standard"] for row in parsed}
    assert by_code["A1"] == "TSBI0202024010101"
    assert by_code["B2"] == "FOLLOW COLORO"
    assert by_code["C3"] is None


def test_upload_xlsx_keeps_color_standard_text():
    wb = Workbook()
    ws = wb.active
    for row in _sample_rows():
        ws.append(row)
    buf = BytesIO()
    wb.save(buf)
    parsed = iter_upload_recipes(buf.getvalue(), "swatch.xlsx")
    by_code = {row["color_code"]: row["color_standard"] for row in parsed}
    assert by_code["A1"] == "TSBI0202024010101"
    assert by_code["B2"] == "FOLLOW COLORO"
    assert by_code["C3"] is None
