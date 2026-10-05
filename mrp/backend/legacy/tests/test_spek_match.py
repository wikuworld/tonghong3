"""Unit: tolerant spek match for MRP outstanding PO."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from spek_match import (
    filter_master_po_by_spek,
    swatch_colors_match,
    swatch_emboss_match,
    thickness_point_in_range,
    yl_spek_reject_reason,
)


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


def test_filter_soho_nubuck_lot_line():
    rows = [
        {
            "id": 53,
            "no_so": "PS26091402",
            "item_name": "SOHO NUBUCK",
            "tebal": "1.2 - 1.4",
            "warna": "BLACK (001)",
            "emboss": "R-231 M",
            "lot_number": "PUMTH26001260914003",
        },
        {
            "id": 54,
            "no_so": "PS26091402",
            "item_name": "SOFT PU COATED LEATHER (MAP-SOFT PU)",
            "tebal": "1.2 - 1.4",
            "warna": "ALUMINA (ADAT)",
            "emboss": "DE-7 SM",
            "lot_number": "PUMTH26001260914004",
        },
    ]
    hits = filter_master_po_by_spek(
        rows,
        material_name="SOHO NUBUCK",
        thickness="1.2-1.4",
        emboss="R-231 M",
    )
    assert [r["id"] for r in hits] == [53]
    assert hits[0]["lot_number"] == "PUMTH26001260914003"


def test_thickness_point_inside_order_range():
    assert thickness_point_in_range("1.2", "1.2 - 1.4")
    assert thickness_point_in_range("1.3", "1.2 - 1.4")
    assert thickness_point_in_range("1.4", "1.2 - 1.4")
    assert not thickness_point_in_range("1.5", "1.2 - 1.4")
    assert not thickness_point_in_range("", "1.2 - 1.4")


def test_yl_pinksicle_rejected_for_core_black():
    reason = yl_spek_reject_reason(
        yl_warna="PINKSICLE (6FS) FLUORESCENT",
        yl_tebal="1.2",
        rencana_warna="CORE BLACK (A0QM)",
        rencana_tebal="1.2 - 1.4",
    )
    assert reason
    assert "tidak cocok" in reason


def test_yl_blank_color_rejected():
    reason = yl_spek_reject_reason(
        yl_warna="",
        yl_tebal="1.2",
        rencana_warna="CORE BLACK (A0QM)",
        rencana_tebal="1.2 - 1.4",
    )
    assert reason
    assert "kosong" in reason


def test_yl_core_black_thickness_accepted():
    assert (
        yl_spek_reject_reason(
            yl_warna="CORE BLACK (A0QM)",
            yl_tebal="1.3",
            rencana_warna="CORE BLACK (A0QM)",
            rencana_tebal="1.2 - 1.4",
        )
        is None
    )


def test_yl_proses_ignores_color_if_thickness_ok():
    assert (
        yl_spek_reject_reason(
            yl_warna="PINKSICLE (6FS) FLUORESCENT",
            yl_tebal="1.3",
            rencana_warna="CORE BLACK (A0QM)",
            rencana_tebal="1.2 - 1.4",
            require_color_match=False,
        )
        is None
    )


def test_yl_proses_still_checks_thickness():
    reason = yl_spek_reject_reason(
        yl_warna="ANY",
        yl_tebal="1.5",
        rencana_warna="CORE BLACK (A0QM)",
        rencana_tebal="1.2 - 1.4",
        require_color_match=False,
    )
    assert reason
    assert "Tebal" in reason
