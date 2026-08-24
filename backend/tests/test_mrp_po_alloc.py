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


def test_unsynced_shape():
    blank = unsynced_mrp_alloc()
    assert blank["mrp_alloc_status"] == MRP_UNSYNCED
    assert blank["mrp_qty_processed"] == ""
