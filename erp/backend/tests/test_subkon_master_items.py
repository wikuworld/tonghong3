"""Unit: import master item SubKon."""

from pathlib import Path

from app.services.subkon_master_items import (
    iter_subkon_rows_from_csv,
    normalize_subkon_row,
)

BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parent
FIXTURE_CSV = Path(__file__).resolve().parent / "fixtures" / "01_Master_Item_SubKon.csv"
SUBKON_CSV = FIXTURE_CSV


def test_normalize_subkon_row_maps_empty_markers():
    row = normalize_subkon_row(
        {
            "item_code": "SUB0003",
            "material_name": "PRO ACTION LEATHER",
            "thickness_range": "-",
            "color": "-",
            "emboss": "-",
        }
    )
    assert row["category"] == "SubKon"
    assert row["item_code"] == "SUB0003"
    assert row["thickness_range"] is None
    assert row["color"] is None
    assert row["emboss"] is None


def test_normalize_subkon_row_comma_thickness():
    row = normalize_subkon_row(
        {
            "item_code": "SUB0017",
            "material_name": "SPLIT SUEDE",
            "thickness_range": "1,5",
            "color": "CORE BLACK (A0QM)",
            "emboss": "",
        }
    )
    assert row["thickness_range"] == "1.4-1.6"


def test_subkon_csv_has_22_rows():
    rows = list(iter_subkon_rows_from_csv(SUBKON_CSV))
    assert len(rows) == 22
    assert rows[0]["item_code"] == "SUB0001"
    assert rows[0]["category"] == "SubKon"
    assert rows[-1]["item_code"] == "SUB0031"
    sub0017 = next(r for r in rows if r["item_code"] == "SUB0017")
    sub0028 = next(r for r in rows if r["item_code"] == "SUB0028")
    assert sub0017["thickness_range"] == "1.4-1.6"
    assert sub0028["thickness_range"] == "1.2-1.4"
