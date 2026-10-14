"""Nama material, ketebalan, dan blok harga diseragamkan untuk pencocokan SO."""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services.buyer_price_aliases import normalize_sheet_cells, split_material_and_thickness
from app.services.buyer_price_import import STANDARD_COLUMN_KEYS, build_price_cells
from app.services.buyer_price_resolve import resolve_unit_price_for_buyer


def test_nike_item_splits_range_and_uses_so_name():
    item, thick = split_material_and_thickness("(OIA) VIRGIN PU 1.2-1.4", "1.2")
    assert item == "VIRGIN HYDRO PU"
    assert thick == "1.2-1.4"
    row = build_price_cells(
        item="(OIA) VIRGIN PU 1.2-1.4",
        thickness="1.2",
        block="SPECIAL",
        white=1.23,
        black=1.28,
        color=1.33,
    )
    assert row["ITEM"] == "VIRGIN HYDRO PU"
    assert row["THICKNESS"] == "1.2-1.4"
    assert row["COLOR"] == "SPECIAL"


def test_product_color_is_not_stored_as_price_block():
    cells = normalize_sheet_cells(
        {"ITEM": "VIRGIN HYDRO PU", "THICKNESS": "1.2-1.4", "COLOR": "BLACK (00A)"}
    )
    assert cells["COLOR"] == ""


def test_range_with_mm_suffix_leaves_material_name():
    item, thick = split_material_and_thickness("Action Pu Coated Leather  1.0-1.6 MM", "1.0-1.6")
    assert item == "Action Pu Coated Leather"
    assert thick == "1.0-1.6"


def test_pm_generic_alias():
    item, _thick = split_material_and_thickness("(PM) GENERIC PU COATED", "")
    assert item == "(PM) GENERIC PU COATED LEATHER"


def test_resolve_so_thickness_prefers_nike_block(monkeypatch):
    rows = [
        build_price_cells(
            item="(OIA) VIRGIN PU 1.2-1.4",
            thickness="1.2",
            block="COMMON",
            white=1.13,
            black=1.18,
            color=1.23,
            fluo=1.38,
            metallic=1.38,
        ),
        build_price_cells(
            item="(OIA) VIRGIN PU 1.2-1.4",
            thickness="1.2",
            block="SPECIAL",
            white=1.23,
            black=1.28,
            color=1.33,
            fluo=1.48,
            metallic=1.48,
        ),
        build_price_cells(
            item="VIRGIN HYDRO PU",
            thickness="1.2-1.4",
            block="BLACK (00A)",
            white=9,
            black=9,
            color=9,
            fluo=9,
            metallic=9,
        ),
    ]
    db = MagicMock()
    lst = SimpleNamespace(id=22, period_start=date(2026, 7, 1), period_end=date(2026, 12, 31))
    db.scalars.return_value.all.return_value = [lst]
    monkeypatch.setattr(
        "app.services.buyer_price_resolve.list_to_api_dict",
        lambda _db, _id: {"rows": rows, "meta_json": {"column_keys": list(STANDARD_COLUMN_KEYS)}},
    )
    monkeypatch.setattr(
        "app.services.buyer_price_resolve.is_outside_banten_factory",
        lambda *_a, **_k: False,
    )
    result = resolve_unit_price_for_buyer(
        db,
        "NIKE",
        material_name="VIRGIN HYDRO PU",
        thickness_text="1.2 - 1.4",
        color_family="color",
        emboss="AR-140",
        as_of=date(2026, 10, 5),
    )
    assert result["matched"] is True
    assert result["unit_price"] == Decimal("1.33")
