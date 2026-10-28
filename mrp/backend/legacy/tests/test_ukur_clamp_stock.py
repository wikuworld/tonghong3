"""Ukur crust di atas stok tetap disimpan utuh; selisih dicatat sebagai Lebih ukur."""

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


class UkurAgainstCapTests(unittest.TestCase):
    def test_crust_keeps_60_9_when_stock_is_60(self):
        applied, overflow = api_routes.split_ukur_against_cap(0, 60.9, 60, clamp=False)
        self.assertAlmostEqual(applied, 60.9, places=3)
        self.assertAlmostEqual(overflow, 0.9, places=3)

    def test_crust_overflow_is_only_the_new_excess(self):
        applied, overflow = api_routes.split_ukur_against_cap(50, 12, 60, clamp=False)
        self.assertAlmostEqual(applied, 12.0, places=3)
        self.assertAlmostEqual(overflow, 2.0, places=3)

    def test_crust_second_measure_does_not_repeat_prior_excess(self):
        applied, overflow = api_routes.split_ukur_against_cap(60.9, 1, 60, clamp=False)
        self.assertAlmostEqual(applied, 1.0, places=3)
        self.assertAlmostEqual(overflow, 1.0, places=3)

    def test_mod_still_clamps_to_capacity(self):
        applied, overflow = api_routes.split_ukur_against_cap(0, 60.9, 60, clamp=True)
        self.assertAlmostEqual(applied, 60.0, places=3)
        self.assertAlmostEqual(overflow, 0.9, places=3)


class KyCloseVarianceTests(unittest.TestCase):
    def test_tutup_sisa_records_kurang_against_stock(self):
        row = api_routes._ky_close_kulit_lebih(50, 60, 60, True)
        self.assertEqual(row["keterangan"], "Kurang")
        self.assertAlmostEqual(row["selisih"], -10.0, places=3)
        self.assertAlmostEqual(row["target_qty"], 60.0, places=3)
        self.assertAlmostEqual(row["actual_qty"], 50.0, places=3)

    def test_return_to_pallet_records_kurang_against_target(self):
        row = api_routes._ky_close_kulit_lebih(50, 60, 60, False)
        self.assertEqual(row["keterangan"], "Kurang")
        self.assertAlmostEqual(row["selisih"], -10.0, places=3)
        self.assertAlmostEqual(row["target_qty"], 60.0, places=3)

    def test_over_measure_close_does_not_add_kurang(self):
        # 60 vs 60.9 stays on the Lebih ukur row from add_ukur, not a Kurang close row.
        self.assertIsNone(api_routes._ky_close_kulit_lebih(60.9, 60, 60, True))


if __name__ == "__main__":
    unittest.main()
