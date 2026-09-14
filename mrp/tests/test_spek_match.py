"""Unit: tolerant spek match for MRP outstanding PO."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from spek_match import filter_master_po_by_spek, swatch_colors_match, swatch_emboss_match


def test_color_match_ignores_code_suffix():
    assert swatch_colors_match("CARGO KHAKI (3HR)", "CARGO KHAKI")
    assert swatch_colors_match("CARGO KHAKI", "CARGO KHAKI (3HR)")


def test_emboss_match_ignores_finish_suffix():
    assert swatch_emboss_match("AR-206 M", "AR-206")


def test_material_match_prefix():
    from spek_match import material_matches

    assert material_matches("VIRGIN  HYDRO PU", "VIRGIN HYDRO PU")
    assert not material_matches("SUEDE X", "VIRGIN HYDRO PU")


def test_filter_master_po_cargo_khaki_case():
    rows = [
        {
            "id": 34,
            "no_po": "PO-THIPM26082603",
            "item_name": "VIRGIN HYDRO PU",
            "tebal": "1.2 - 1.4",
            "warna": "CARGO KHAKI (3HR)",
            "emboss": "AR-206 M",
            "color_swatch": "3HR",
            "qty_outstanding": 15000,
        },
        {
            "id": 33,
            "no_po": "PO-THIPM26082601",
            "item_name": "VIRGIN HYDRO PU",
            "tebal": "1.2 - 1.4",
            "warna": "CARGO KHAKI (3HR)",
            "emboss": "R-102 M",
            "color_swatch": "3HR",
            "qty_outstanding": 15000,
        },
    ]
    hits = filter_master_po_by_spek(
        rows,
        material_name="VIRGIN HYDRO PU",
        thickness="1.2 - 1.4",
        color="CARGO KHAKI",
        emboss="AR-206 M",
    )
    assert [r["id"] for r in hits] == [34]
