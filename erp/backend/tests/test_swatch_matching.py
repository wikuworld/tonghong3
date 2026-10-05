"""Unit test normalisasi match warna/emboss swatch vs master item PO."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.services.color_swatch import (
    assert_swatch_recipe_matches_line,
    filter_swatch_recipes_by_dimensions,
    normalize_swatch_color_name,
    normalize_swatch_material_name,
    swatch_colors_match,
    swatch_emboss_code,
    swatch_emboss_match,
    swatch_materials_match,
    swatch_recipe_mismatch_fields,
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
    assert swatch_colors_match("PINKSICLE (6FS) FLUORESCENT", "PINK SICLE")
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


def test_filter_keeps_color_code_hit_when_emboss_differs():
    rows = [
        _FakeRecipe(
            material_name="VIRGIN HYDRO PU",
            color_name="PINK SICLE",
            color_code="6FS",
            emboss="AR-121",
            color_standard="TMSL043",
        ),
        _FakeRecipe(
            material_name="VIRGIN HYDRO PU",
            color_name="FIRE RED",
            color_code="64D",
            emboss="R-53",
            color_standard="OTHER",
        ),
    ]
    out = filter_swatch_recipes_by_dimensions(
        rows,
        material_name="VIRGIN HYDRO PU",
        color_name="PINKSICLE (6FS) FLUORESCENT",
        emboss="AR-33 M",
    )
    assert [r.color_standard for r in out] == ["TMSL043"]


def test_active_pink_recipe_rejects_core_black_line():
    bad = swatch_recipe_mismatch_fields(
        recipe_material="GENERIC PU COATED LEATHER",
        recipe_color="ACTIVE PINK",
        recipe_emboss="DE-73",
        material_name="ACTION LEATHER",
        color="CORE BLACK (A0QM)",
        emboss="AW-44 SG",
    )
    assert set(bad) == {"material", "warna", "emboss"}


def test_matching_core_black_recipe_accepted():
    assert (
        swatch_recipe_mismatch_fields(
            recipe_material="ACTION LEATHER",
            recipe_color="CORE BLACK",
            recipe_emboss="AW-44 SG",
            material_name="ACTION LEATHER",
            color="CORE BLACK (A0QM)",
            emboss="AW-44",
        )
        == []
    )


def test_assert_swatch_recipe_raises_on_mismatch():
    db = MagicMock()
    db.get.return_value = SimpleNamespace(
        material_name="GENERIC PU COATED LEATHER",
        color_name="ACTIVE PINK",
        emboss="DE-73",
        is_active=True,
    )
    with pytest.raises(HTTPException) as exc:
        assert_swatch_recipe_matches_line(
            db,
            recipe_id=3584,
            material_name="ACTION LEATHER",
            color="CORE BLACK (A0QM)",
            emboss="AW-44 SG",
        )
    assert exc.value.status_code == 400


def test_assert_swatch_recipe_allows_match():
    db = MagicMock()
    db.get.return_value = SimpleNamespace(
        material_name="ACTION LEATHER",
        color_name="CORE BLACK",
        emboss="AW-44 SG",
        is_active=True,
    )
    assert_swatch_recipe_matches_line(
        db,
        recipe_id=1,
        material_name="ACTION LEATHER",
        color="CORE BLACK (A0QM)",
        emboss="AW-44 SG",
    )
