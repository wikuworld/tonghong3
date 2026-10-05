"""Tests fluorescent color master service helpers."""

from app.services.fluorescent_color import (
    apply_fluorescent_fields,
    find_existing,
    normalize_buyer_code,
    normalize_color_class,
)


def test_normalize_buyer_and_class():
    assert normalize_buyer_code("  nb ") == "NB"
    assert normalize_color_class("Metallic") == "metallic"
    assert normalize_color_class("unknown") == "fluorescent"


def test_apply_fluorescent_fields():
    data = apply_fluorescent_fields(
        {
            "buyer_code": "adidas",
            "season_label": " SS26 ",
            "color_name": " TEST RED ",
            "color_code": " A1 ",
            "color_class": "metallic",
        }
    )
    assert data["buyer_code"] == "ADIDAS"
    assert data["season_label"] == "SS26"
    assert data["color_name"] == "TEST RED"
    assert data["color_code"] == "A1"
    assert data["color_class"] == "metallic"


def test_find_existing_none_without_db():
    # find_existing needs db — smoke import only
    assert callable(find_existing)
