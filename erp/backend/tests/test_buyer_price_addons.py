"""Addon wajib harga buyer dari flag master item."""

from types import SimpleNamespace

from app.services.buyer_price_addons import (
    format_required_price_gaps,
    missing_addons_for_cells,
    missing_addons_for_sheet,
    missing_required_prices,
)


def _item(**kwargs):
    base = {
        "material_name": "VIRGIN HYDRO PU",
        "thickness_range": "1.2-1.4",
        "flag_color_black": False,
        "flag_color": False,
        "flag_flourasent": False,
        "flag_metalic": False,
        "flag_emboss": False,
        "flag_special_emboss": False,
    }
    base.update(kwargs)
    return SimpleNamespace(**base)


def test_union_flags_zero_is_entered_blank_is_missing():
    items = [
        _item(flag_color_black=True),
        _item(flag_flourasent=True, flag_color_black=False),
    ]
    cells = {
        "ITEM": " virgin hydro pu ",
        "THICKNESS": "1.2-1.4",
        "COLOR BLACK": 0,
        "FLOURASENT": "",
        "METALIC": 0.1,
    }
    assert missing_addons_for_cells(cells, items) == ["FLOURASENT"]


def test_other_material_or_thickness_does_not_require():
    items = [_item(material_name="ECO", thickness_range="1.0-1.2", flag_emboss=True)]
    cells = {"ITEM": "VIRGIN HYDRO PU", "THICKNESS": "1.2-1.4"}
    assert missing_addons_for_cells(cells, items) == []


def test_flag_off_does_not_require_even_when_empty():
    cells = {"ITEM": "VIRGIN HYDRO PU", "THICKNESS": "1.2-1.4", "COLOR COLOR": ""}
    assert missing_addons_for_cells(cells, [_item()]) == []


def test_required_prices_only_color_white():
    items = [_item(flag_color_black=True)]
    cells = {"ITEM": "VIRGIN HYDRO PU", "THICKNESS": "1.2-1.4", "COLOR WHITE": "", "COLOR BLACK": 0}
    assert missing_required_prices(cells, items) == ["COLOR WHITE"]
    assert missing_required_prices({**cells, "COLOR WHITE": 1.5}, items) == []
    assert missing_required_prices({"ITEM": ""}, items) == []
    message = format_required_price_gaps([cells], items)
    assert message.startswith("Baris 1 (VIRGIN HYDRO PU):")
    assert "COLOR WHITE" in message


def test_sheet_overview_unions_missing_addons():
    items = [_item(flag_metalic=True), _item(thickness_range="1.4-1.6", flag_emboss=True)]
    rows = [
        SimpleNamespace(cells={"ITEM": "VIRGIN HYDRO PU", "THICKNESS": "1.2-1.4", "METALIC": 1}),
        SimpleNamespace(cells={"ITEM": "VIRGIN HYDRO PU", "THICKNESS": "1.4-1.6", "EMBOSS": ""}),
        SimpleNamespace(cells={"ITEM": "VIRGIN HYDRO PU", "THICKNESS": "1.2-1.4", "METALIC": ""}),
    ]
    assert missing_addons_for_sheet(rows, items) == ["EMBOSS", "METALIC"]
