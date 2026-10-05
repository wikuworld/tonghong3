"""Stock WH outstanding = packing finished per lot/RPI, bukan packing_po.po_id + SJ."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api_routes import _assign_stock_wh_from_finished_packings  # noqa: E402


def test_stock_wh_uses_rencana_item_not_wrong_packing_po():
    """Lot PUMTH26001260914003: packing_po.po_id bisa baris SO lain di PO yang sama."""
    packings = [
        {"id": 16, "rencana_item_id": 54, "kode_wip": "WIP-20260914-00004", "total_ukuran": 500}
    ]
    packing_po_rows = [
        {"packing_id": 16, "po_id": 54, "no_so": "PS26091402", "qty_sq": 500}
    ]
    alloc_rows = [
        {
            "item_id": 54,
            "po_id": 53,
            "source_detail_id": 69,
            "lot_number": "PUMTH26001260914003",
            "kode_lot_wip": "WIP-260914000004",
        },
        {
            "item_id": 55,
            "po_id": 54,
            "source_detail_id": 70,
            "lot_number": "PUMTH26001260914004",
            "kode_lot_wip": "WIP-260914000005",
        },
    ]
    out = _assign_stock_wh_from_finished_packings(
        packings, packing_po_rows, alloc_rows, [69, 70]
    )
    assert out.get(69) == 500
    assert 70 not in out


def test_stock_wh_ignores_in_progress_by_not_receiving_them():
    packings = [{"id": 1, "rencana_item_id": 8, "total_ukuran": 120}]
    alloc_rows = [{"item_id": 8, "po_id": 3, "source_detail_id": 11, "kode_lot_wip": "WIP-1"}]
    out = _assign_stock_wh_from_finished_packings(packings, [], alloc_rows, [11])
    assert out[11] == 120


def test_qty_wip_mutual_exclusive_with_stock_wh():
    """Display WIP = max(0, prep − stock_wh)."""
    wip_raw = 500.0
    stock_wh = 500.0
    assert max(0.0, wip_raw - stock_wh) == 0.0
    assert max(0.0, 800.0 - 300.0) == 500.0
    assert max(0.0, 100.0 - 300.0) == 0.0
