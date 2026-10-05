"""Unit tests for PU / Suide master item import."""

from pathlib import Path

from app.services.pu_suede_master_items import (
    infer_pu_suede_category,
    iter_pu_suede_rows_from_csv,
    normalize_pu_suede_row,
    resolve_pu_suede_category,
)

FIXTURE_CSV = Path(__file__).resolve().parent / "fixtures" / "pu_suede_sample.csv"


def test_infer_pu_suede_category_from_material_name():
    assert infer_pu_suede_category("VIRGIN HYDRO PU") == "PU"
    assert infer_pu_suede_category("SPLIT SUEDE") == "Suide"


def test_resolve_pu_suede_category_prefers_explicit_column():
    row = {"category": "PU", "material_name": "SPLIT SUEDE"}
    assert resolve_pu_suede_category(row, row["material_name"]) == "PU"


def test_normalize_pu_suede_row_maps_columns():
    row = normalize_pu_suede_row(
        {
            "KODE BARANG": "FG00001",
            "THICKNESS": "1.2-1.4",
            "MATERIAL NAME": "VIRGIN HYDRO PU",
            "EMBOSS": "AR-167 DM",
            "COLOR": "BLACK (00A)",
        }
    )
    assert row["item_code"] == "FG00001"
    assert row["category"] == "PU"
    assert row["thickness_range"] == "1.2-1.4"


def test_pu_suede_fixture_csv_has_rows():
    rows = list(iter_pu_suede_rows_from_csv(FIXTURE_CSV))
    assert len(rows) == 3
    assert rows[0]["item_code"] == "FG00001"
    assert rows[2]["category"] == "Suide"
