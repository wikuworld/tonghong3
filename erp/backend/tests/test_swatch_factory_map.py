"""Test pemetaan factory swatch → customer."""

from app.services.swatch_factory_map import (
    extract_customer_code_from_color_standard,
    resolve_customer_code_for_swatch,
)


def test_extract_customer_code_from_color_standard():
    assert extract_customer_code_from_color_standard("TMAD0022020101201") == "AD002"
    assert extract_customer_code_from_color_standard("TMCS0052021080601") == "CS005"
    assert extract_customer_code_from_color_standard("TMSD0462021021501") == "SD047"


def test_resolve_customer_code_prefers_color_standard_over_factory():
    assert (
        resolve_customer_code_for_swatch(
            "CHANGSHIN",
            color_standard="TMCS0052021080601",
        )
        == "CS005"
    )


def test_resolve_customer_code_factory_alias():
    assert resolve_customer_code_for_swatch("FENGTAY WEST") == "FT006"
    assert resolve_customer_code_for_swatch("NIKOMAS IY") == "NS020"
    assert resolve_customer_code_for_swatch("METRO NB") == "MP033"
    assert resolve_customer_code_for_swatch("YMUV") == "YC027"
