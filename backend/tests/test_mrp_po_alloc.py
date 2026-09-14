from unittest.mock import patch

from app.services.mrp_po_alloc import (
    MRP_UNSYNCED,
    enrich_outstanding_mrp_alloc,
    parse_mrp_alloc_row,
    unsynced_mrp_alloc,
)


def test_parse_mrp_alloc_row_remaining():
    out = parse_mrp_alloc_row(
        {"status": "partial", "qty_order": 2000, "qty_processed": 1, "source_detail_id": 1}
    )
    assert out["mrp_alloc_status"] == "partial"
    assert out["mrp_qty_processed"] == "1"
    assert out["mrp_qty_remaining"] == "1999"


def test_parse_mrp_alloc_row_unknown_status_is_unsynced():
    out = parse_mrp_alloc_row({"status": "", "qty_order": 10, "qty_processed": 2})
    assert out["mrp_alloc_status"] == MRP_UNSYNCED
    assert out["mrp_qty_remaining"] == ""


def test_enrich_uses_fetch_and_marks_missing_unsynced():
    rows = [{"po_detail_id": 1}, {"po_detail_id": 99}]
    found = {
        1: {
            "mrp_alloc_status": "partial",
            "mrp_qty_processed": "1",
            "mrp_qty_remaining": "1999",
        }
    }
    with patch("app.services.mrp_po_alloc.fetch_mrp_alloc_by_detail_ids", return_value=found):
        enrich_outstanding_mrp_alloc(rows)
    assert rows[0]["mrp_alloc_status"] == "partial"
    assert rows[0]["mrp_qty_remaining"] == "1999"
    assert rows[1]["mrp_alloc_status"] == MRP_UNSYNCED


def test_parse_mrp_alloc_row_ship_remaining():
    out = parse_mrp_alloc_row(
        {
            "status": "partial",
            "qty_order": 100,
            "qty_processed": 20,
            "qty_balance_erp": 70,
        }
    )
    assert out["mrp_qty_remaining"] == "80"
    assert out["mrp_qty_ship_remaining"] == "70"


def test_unsynced_shape():
    blank = unsynced_mrp_alloc()
    assert blank["mrp_alloc_status"] == MRP_UNSYNCED
    assert blank["mrp_qty_processed"] == ""
    assert blank["mrp_qty_ship_remaining"] == ""
    assert blank["mrp_qty_wip"] == ""


def test_parse_mrp_alloc_row_qty_wip():
    out = parse_mrp_alloc_row(
        {"status": "partial", "qty_order": 800, "qty_processed": 500, "qty_wip": 200}
    )
    assert out["mrp_qty_processed"] == "500"
    assert out["mrp_qty_wip"] == "200"


def test_qty_wip_absent_or_invalid_is_zero():
    assert parse_mrp_alloc_row({"status": "outstanding", "qty_order": 10})["mrp_qty_wip"] == "0"
    noisy = parse_mrp_alloc_row({"status": "partial", "qty_order": 10, "qty_wip": "abc"})
    assert noisy["mrp_qty_wip"] == "0"


def test_qty_wip_blank_when_unsynced():
    out = parse_mrp_alloc_row({"status": "", "qty_order": 10, "qty_wip": 5})
    assert out["mrp_qty_wip"] == ""


def test_parse_mrp_alloc_row_stock_wh():
    out = parse_mrp_alloc_row(
        {"status": "partial", "qty_order": 800, "qty_processed": 500, "stock_wh_qty": 120}
    )
    assert out["stock_wh_qty"] == "120"


def test_enrich_overlays_stock_wh_from_mrp():
    rows = [{"po_detail_id": 1, "stock_wh_qty": "5"}]
    found = {
        1: {
            "mrp_alloc_status": "partial",
            "mrp_qty_processed": "1",
            "mrp_qty_remaining": "1999",
            "mrp_qty_ship_remaining": "",
            "mrp_qty_wip": "200",
            "stock_wh_qty": "150",
        }
    }
    with patch("app.services.mrp_po_alloc.fetch_mrp_alloc_by_detail_ids", return_value=found):
        enrich_outstanding_mrp_alloc(rows)
    assert rows[0]["stock_wh_qty"] == "150"
    assert rows[0]["mrp_qty_wip"] == "200"
