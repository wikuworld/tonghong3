"""Unit test normalisasi match warna/emboss swatch vs master item PO."""

from app.services.color_swatch import (
    filter_swatch_recipes_by_dimensions,
    normalize_swatch_color_name,
    normalize_swatch_material_name,
    swatch_colors_match,
    swatch_emboss_code,
    swatch_emboss_match,
    swatch_materials_match,
)


class _FakeRecipe:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def test_normalize_swatch_color_name_strips_suffix():
    assert normalize_swatch_color_name("WOLF GREY (01V)") == "wolf grey"
    assert normalize_swatch_color_name("WASHED CORAL (6JE)") == "washed coral"


def test_swatch_emboss_code_strips_description():
    assert swatch_emboss_code("AR-167 (DEEP MATTE)") == "AR-167"
    assert swatch_emboss_code("DE-73 (SEMI MATTE)") == "DE-73"
    assert swatch_emboss_code("AR-167 DM") == "AR-167"


def test_swatch_colors_match_form_vs_master():
    assert swatch_colors_match("WOLF GREY (01V)", "WOLF GREY")
    assert swatch_colors_match("WASHED CORAL (6JE)", "WASHED CORAL")
    assert not swatch_colors_match("ANTOMIC VIOLET", "WOLF GREY")


def test_swatch_emboss_match_form_vs_master():
    assert swatch_emboss_match("AR-167 (DEEP MATTE)", "AR-167")
    assert swatch_emboss_match("DE-73 (SEMI MATTE)", "DE-73 SM")
    assert swatch_emboss_match("AR-20 M", "AR-20 M")
    assert swatch_emboss_match("R-8 (SEMI GLOSS)", "R-8 M")
    assert swatch_emboss_code("UM-34T (SEMI MATTE)") == "UM-34T"
    assert swatch_emboss_match("UM-34T (SEMI MATTE)", "UM-34 SM")


def test_swatch_material_match_pm_generic():
    assert normalize_swatch_material_name("(PM) GENERIC PU COATED LEATHER") == "generic pu"
    assert swatch_materials_match(
        "(PM) GENERIC PU COATED LEATHER",
        "(PM) GENERIC PU COATED",
    )


def test_filter_swatch_recipes_by_dimensions():
    rows = [
        _FakeRecipe(
            material_name="VIRGIN HYDRO PU",
            color_name="WOLF GREY",
            emboss="AR-167",
            color_standard="TM001",
        ),
        _FakeRecipe(
            material_name="VIRGIN HYDRO PU",
            color_name="WASHED CORAL",
            emboss="AR-167 DM",
            color_standard="TM002",
        ),
    ]
    out = filter_swatch_recipes_by_dimensions(
        rows,
        material_name="VIRGIN HYDRO PU",
        color_name="WOLF GREY (01V)",
        emboss="AR-167 (DEEP MATTE)",
    )
    assert len(out) == 1
    assert out[0].color_standard == "TM001"
