"""Unit: opsi rencana produksi dari color_swatch_recipes."""

from __future__ import annotations

from types import SimpleNamespace

from app.services.mrp_color_swatch_bridge import (
    combination_from_swatch,
    options_for_rencana,
)


def _recipe(**kwargs):
    defaults = {
        "id": 1,
        "material_name": "PU COATED LEATHER",
        "emboss": "DE-73",
        "color_name": "METAL GREY",
        "factory_key": "NIKOMAS",
        "backing": "WHITE",
        "buyer_code": "NIKE",
        "color_code": "01V",
        "csi_color_master_id": None,
        "is_active": True,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_options_for_rencana_builds_cascading_maps():
    recipes = [
        _recipe(),
        _recipe(id=2, emboss="DE-7", color_name="DASH GREEB", factory_key="PANARUB", backing="WHITE"),
    ]
    body = options_for_rencana(None, recipes, [])
    assert body["source"] == "color_swatch_recipes"
    assert "PU COATED LEATHER" in body["materials"]
    assert "DE-73" in body["embosses_by_material"]["PU COATED LEATHER"]
    key = "pu coated leather\x1ede-73"
    assert "METAL GREY" in body["colors_by_material_emboss"][key]
    assert body["color_labels"]["METAL GREY"] == "METAL GREY"


def test_options_label_uses_csi_when_linked():
    recipes = [_recipe(csi_color_master_id=9, color_name="WOLF GREY", color_code="01V")]
    body = options_for_rencana(None, recipes, [])
    key = "pu coated leather\x1ede-73"
    assert "WOLF GREY" in body["colors_by_material_emboss"][key]
    assert body["color_labels"]["WOLF GREY"] == "WOLF GREY (01V)"


def test_combination_from_swatch_returns_factory_and_backer():
    recipes = [_recipe()]
    hits = combination_from_swatch(
        None,
        recipes,
        [],
        material_name="PU COATED LEATHER",
        color="METAL GREY",
        emboss="DE-73",
    )
    assert len(hits) == 1
    assert hits[0]["color_swatch"] == "NIKOMAS"
    assert hits[0]["backer"] == "WHITE"


def test_combination_prefers_csi_linked_and_color_code():
    recipes = [
        _recipe(id=1, factory_key="PANARUB", csi_color_master_id=None, color_code="01V"),
        _recipe(id=2, factory_key="NIKOMAS", csi_color_master_id=11, color_code="01V"),
        _recipe(id=3, factory_key="HWP", csi_color_master_id=12, color_code="99Z"),
    ]
    hits = combination_from_swatch(
        None,
        recipes,
        [],
        material_name="PU COATED LEATHER",
        color="METAL GREY",
        emboss="DE-73",
        color_code="01V",
    )
    assert [h["factory_key"] for h in hits] == ["NIKOMAS", "PANARUB"]
    assert hits[0]["csi_color_master_id"] == 11
