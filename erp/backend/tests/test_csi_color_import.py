"""Tes mapping sheet Excel CSI → buyer + upsert."""

from pathlib import Path

from app.services.csi_color import SHEET_BUYER, apply_csi_fields, parse_csi_workbook


def test_sheet_buyer_mapping():
    assert SHEET_BUYER["NB"] == "NB"
    assert SHEET_BUYER["NIKE CSI"] == "NIKE"
    assert SHEET_BUYER["UA CSI"] == "UA"
    assert SHEET_BUYER["ADIDAS"] == "ADIDAS"


def test_apply_csi_fields_normalizes():
    data = apply_csi_fields({"buyer_code": " nike ", "color_code": " 00A ", "color_name": " BLACK "})
    assert data["buyer_code"] == "NIKE"
    assert data["color_code"] == "00A"
    assert data["color_name"] == "BLACK"


def test_parse_csi_workbook_if_present():
    path = Path("/app/dokumentasi/CSI ALL BUYER.xlsx")
    if not path.is_file():
        path = Path(__file__).resolve().parents[2] / "dokumentasi" / "CSI ALL BUYER.xlsx"
    if not path.is_file():
        return
    rows = parse_csi_workbook(path)
    assert rows
    buyers = {r["buyer_code"] for r in rows}
    assert {"NIKE", "UA", "NB", "ADIDAS"} <= buyers
    assert all(r["color_code"] for r in rows)
