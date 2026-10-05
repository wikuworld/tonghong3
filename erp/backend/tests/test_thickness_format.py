"""Unit: format ketebalan rentang standar."""

from decimal import Decimal

from app.services.thickness_format import (
    canonical_thickness_range,
    display_thickness_range,
    display_thickness_with_mm,
    single_value_to_bucket,
    thickness_ranges_equivalent,
)
from app.services.master_item_dimensions import (
    distinct_thicknesses,
    master_item_thickness_display,
    thickness_matches,
)
from app.models import MasterItem


def test_single_mm_maps_to_standard_bucket() -> None:
    assert single_value_to_bucket(Decimal("1.24")) == "1.2-1.4"
    assert single_value_to_bucket(Decimal("1.46")) == "1.4-1.6"
    assert single_value_to_bucket(Decimal("1.02")) == "1.0-1.2"


def test_canonical_and_display() -> None:
    assert canonical_thickness_range("1.24") == "1.2-1.4"
    assert canonical_thickness_range("1,5") == "1.4-1.6"
    assert canonical_thickness_range("1,3") == "1.2-1.4"
    assert canonical_thickness_range("-") == ""
    assert display_thickness_range("1.24") == "1.2 - 1.4"
    assert display_thickness_range("1.2-1.4") == "1.2 - 1.4"
    assert display_thickness_range("1.2 - 1.4") == "1.2 - 1.4"
    assert display_thickness_range("1.2-1.4MM") == "1.2 - 1.4"
    assert display_thickness_with_mm("1.2-1.4") == "1.2 - 1.4 mm"
    assert display_thickness_with_mm("1.2-1.4MM") == "1.2 - 1.4 mm"
    assert display_thickness_with_mm("1.4") == "1.2 - 1.4 mm"
    assert display_thickness_with_mm("") == ""


def test_thickness_equivalent() -> None:
    assert thickness_ranges_equivalent("1.24", "1.2 - 1.4")
    assert thickness_ranges_equivalent("1.2-1.4", "1.2 - 1.4")


def test_master_item_dimensions_use_buckets() -> None:
    row = MasterItem(
        id=1,
        item_code="FG1",
        material_name="VIRGIN HYDRO PU",
        thickness_range="1.24",
        color="BLACK",
    )
    assert master_item_thickness_display(row) == "1.2-1.4"
    assert thickness_matches(row, "1.2 - 1.4")
    assert distinct_thicknesses([row], "VIRGIN HYDRO PU") == ["1.2 - 1.4"]
