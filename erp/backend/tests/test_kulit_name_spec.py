"""Urai tebal dan warna dari nama master kulit."""

from app.services.kulit_name_spec import kulit_spec_from_name


def test_light_brown_decimal():
    spec = kulit_spec_from_name("LIGHT BROWN 1.02")
    assert spec == {"thickness": "1.02", "color": "LIGHT BROWN"}


def test_grey_decimal():
    spec = kulit_spec_from_name("GREY 1.02")
    assert spec == {"thickness": "1.02", "color": "GREY"}


def test_short_code_is_not_a_color():
    spec = kulit_spec_from_name("01V 1.02")
    assert spec == {"thickness": "1.02", "color": None}


def test_thickness_with_mm_suffix():
    spec = kulit_spec_from_name("Dark Blue 1.2mm")
    assert spec == {"thickness": "1.2", "color": "Dark Blue"}


def test_range_keeps_both_ends():
    spec = kulit_spec_from_name("CACAO-WOW 1.2-1.4")
    assert spec == {"thickness": "1.2-1.4", "color": "CACAO-WOW"}


def test_code_only_name_is_left_alone():
    spec = kulit_spec_from_name("KLT-001")
    assert spec == {"thickness": None, "color": None}
    assert kulit_spec_from_name("Dark Brown") == {"thickness": None, "color": None}
    assert kulit_spec_from_name("RED 03 UPD") == {"thickness": None, "color": None}


def test_color_after_millimeter():
    spec = kulit_spec_from_name("RECYCLE LEATHER, 1.2MM BLACK")
    assert spec == {"thickness": "1.2", "color": "BLACK"}


def test_hyphen_code_only_fills_thickness():
    spec = kulit_spec_from_name("2CT-1.34")
    assert spec == {"thickness": "1.34", "color": None}
