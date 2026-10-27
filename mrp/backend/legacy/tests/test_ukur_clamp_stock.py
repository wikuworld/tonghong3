"""Ukur melebihi stok YL di-clamp; selisih dicatat sebagai Lebih ukur."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[1]
BACKEND = Path(__file__).resolve().parents[2]
for p in (str(BACKEND), str(ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

import api_routes  # noqa: E402


class RecordLebihUkurTests(unittest.TestCase):
    def test_inserts_lebih_ukur_row(self):
        cur = MagicMock()
        api_routes._record_lebih_ukur(
            cur,
            rencana_item_id=11,
            persiapan_id=22,
            ky_id=33,
            kode_palet="PAL-1",
            kode_yl="YL-1",
            cap_qty=60.0,
            raw_total=60.9,
            overflow=0.9,
        )
        sql, params = cur.execute.call_args.args
        self.assertIn("tbl_kulit_lebih", sql)
        self.assertEqual(params[0], 11)
        self.assertEqual(params[1], 22)
        self.assertEqual(params[2], 33)
        self.assertEqual(params[5], 60.0)
        self.assertEqual(params[6], 60.9)
        self.assertEqual(params[7], 0.9)
        self.assertEqual(params[8], "Lebih ukur")

    def test_skips_when_overflow_zero(self):
        cur = MagicMock()
        api_routes._record_lebih_ukur(
            cur,
            rencana_item_id=1,
            persiapan_id=2,
            ky_id=3,
            kode_palet="P",
            kode_yl="Y",
            cap_qty=60.0,
            raw_total=60.0,
            overflow=0.0,
        )
        cur.execute.assert_not_called()


class ClampMathTests(unittest.TestCase):
    def test_60_vs_60_9(self):
        prev_actual = 0.0
        size_val = 60.9
        cap = 60.0
        room = max(0.0, round(cap - prev_actual, 3))
        applied = round(min(size_val, room), 3) if room > 1e-9 else 0.0
        overflow = round(max(0.0, size_val - applied), 3)
        self.assertEqual(applied, 60.0)
        self.assertAlmostEqual(overflow, 0.9, places=3)

    def test_partial_room(self):
        prev_actual = 50.0
        size_val = 12.0
        cap = 60.0
        room = max(0.0, round(cap - prev_actual, 3))
        applied = round(min(size_val, room), 3)
        overflow = round(max(0.0, size_val - applied), 3)
        self.assertEqual(applied, 10.0)
        self.assertEqual(overflow, 2.0)


if __name__ == "__main__":
    unittest.main()
