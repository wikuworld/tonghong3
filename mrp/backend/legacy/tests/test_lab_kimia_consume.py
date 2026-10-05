"""Unit tests for lab → stok kimia lapangan FIFO consume."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = Path(__file__).resolve().parents[2]
for p in (str(ROOT), str(BACKEND)):
    if p not in sys.path:
        sys.path.insert(0, p)

from dual_gudang import GUDANG_LAPANGAN  # noqa: E402


class _FakeCursor:
    def __init__(self, lots):
        self.lots = list(lots)
        self.executed = []
        self.lastrowid = 0

    def execute(self, sql, params=None):
        self.executed.append((sql, params))
        if "FROM tbl_stok_kimia_in" in sql:
            self._fetch = list(self.lots)
        elif "INSERT INTO tbl_stok_kimia_out" in sql:
            self.lastrowid += 1
        elif "UPDATE tbl_stok_kimia_in" in sql:
            lot_id = params[1]
            new_sisa = params[0]
            for lot in self.lots:
                if lot["id"] == lot_id:
                    lot["qty_sisa"] = new_sisa

    def fetchall(self):
        return getattr(self, "_fetch", [])


def test_kimia_consume_lapangan_fifo_splits_across_lots():
    from api_routes import _kimia_consume_lapangan_fifo

    cur = _FakeCursor(
        [
            {
                "id": 1,
                "kode_internal": "BC-K-001",
                "kimia_id": 10,
                "erp_material_id": 10,
                "kode_material": "KIM-A",
                "nama_material": "Kim A",
                "qty_sisa": 3.0,
            },
            {
                "id": 2,
                "kode_internal": "BC-K-002",
                "kimia_id": 10,
                "erp_material_id": 10,
                "kode_material": "KIM-A",
                "nama_material": "Kim A",
                "qty_sisa": 5.0,
            },
        ]
    )
    outs = _kimia_consume_lapangan_fifo(
        cur,
        kode_kimia="KIM-A",
        code_match="KIM-A",
        qty_needed=6.0,
        kode_wip="WIP-1",
        keterangan="Lab lot LW-001",
        tanggal="2026-09-23",
    )
    assert len(outs) == 2
    assert outs[0]["qty"] == 3.0
    assert outs[1]["qty"] == 3.0
    assert cur.lots[0]["qty_sisa"] == 0
    assert cur.lots[1]["qty_sisa"] == 2.0
    assert any(GUDANG_LAPANGAN in (p or ()) for _, p in cur.executed if p)
