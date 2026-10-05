"""Unit: extract kode/qualifier warna item & dual COLORO."""

from types import SimpleNamespace

from app.services.color_code import (
    apply_item_color_extract,
    csi_color_label,
    extract_item_color_code,
    extract_item_color_qualifier,
    parse_dual_color_code,
)


def test_extract_simple_paren():
    assert extract_item_color_code("BLACK (00A)") == "00A"
    assert extract_item_color_code("WOLF GREY (01V)") == "01V"


def test_extract_suffix_after_paren():
    assert extract_item_color_code("UNIVERSITY RED (65N) FLUORESCENT") == "65N"
    assert extract_item_color_code("GREEN (020A) PEARLIZED") == "020A"
    assert extract_item_color_code("BLAST RED COLORO (011-50-32) FLUORESCENT") == "011-50-32"


def test_extract_no_paren():
    assert extract_item_color_code("0AJ/6CD") is None
    assert extract_item_color_code("CLOUD DANCER") is None
    assert extract_item_color_code("") is None
    assert extract_item_color_code(None) is None


def test_extract_qualifier():
    assert extract_item_color_qualifier("UNIVERSITY RED (65N) FLUORESCENT") == "FLUORESCENT"
    assert extract_item_color_qualifier("GREEN (020A) PEARLIZED") == "PEARLIZED"
    assert extract_item_color_qualifier("BLACK (00A)") is None


def test_parse_dual_coloro_nb():
    dual = parse_dual_color_code("124-91-00 (NB103)")
    assert dual is not None
    assert dual.alias_code == "124-91-00"
    assert dual.csi_code == "NB103"


def test_parse_dual_metallic_not_csi():
    dual = parse_dual_color_code("0AJ (Mettalic)")
    assert dual is not None
    assert dual.alias_code == "0AJ"
    assert dual.csi_code is None


def test_csi_color_label():
    assert csi_color_label("WOLF GREY", "01V") == "WOLF GREY (01V)"
    assert csi_color_label("WOLF GREY (01V)", "01V") == "WOLF GREY (01V)"
    assert csi_color_label("BLACK", None) == "BLACK"


def test_apply_item_color_extract_keeps_display_name():
    row = SimpleNamespace(color="UNIVERSITY RED (65N) FLUORESCENT", color_code=None, color_qualifier=None)
    apply_item_color_extract(row)
    assert row.color == "UNIVERSITY RED (65N) FLUORESCENT"
    assert row.color_code == "65N"
    assert row.color_qualifier == "FLUORESCENT"
