"""Ukur KY memotong stok YL; tanpa sisa = OUT sisa sebagai adjustment."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import _consume_yl_for_ky_session  # noqa: E402
import app as mrp_app  # noqa: E402


def _ky(**overrides):
    row = {
        "id": 7,
        "yl_consumed": 0,
        "qty_consumed": 0,
        "actual_qty": 12.0,
        "kode_yl": "YL-1",
        "kode_palet": "PAL-1",
        "tidak_ada_sisa": 0,
    }
    row.update(overrides)
    return row


class ConsumeYlForKySessionTests(unittest.TestCase):
    def test_ukur_consumes_measured_qty_only(self):
        calls = []

        def fake_stock(cur, palet, yl, qty, tanggal=None, keterangan=None):
            calls.append({"qty": float(qty), "keterangan": keterangan})
            return float(qty)

        cur = MagicMock()
        with patch.object(mrp_app, "_consume_yl_stock", fake_stock):
            total = _consume_yl_for_ky_session(cur, _ky(), {"kode_wip": "WIP-99"})
        self.assertEqual(total, 12.0)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["qty"], 12.0)
        self.assertIn("Keluar proses persiapan", calls[0]["keterangan"] or "")
        self.assertNotIn("tidak ada sisa", (calls[0]["keterangan"] or "").lower())
        cur.execute.assert_called()
        update_sql, update_params = cur.execute.call_args.args
        self.assertIn("yl_consumed=1", update_sql)
        self.assertEqual(update_params, (12.0, 7))

    def test_tidak_ada_sisa_outs_remainder_as_adjustment(self):
        calls = []

        def fake_stock(cur, palet, yl, qty, tanggal=None, keterangan=None):
            calls.append({"qty": float(qty), "keterangan": keterangan})
            return float(qty)

        cur = MagicMock()
        cur.fetchone.return_value = {"qty": 8.0}
        with patch.object(mrp_app, "_consume_yl_stock", fake_stock):
            total = _consume_yl_for_ky_session(
                cur,
                _ky(tidak_ada_sisa=1),
                {"kode_wip": "WIP-99"},
            )
        self.assertEqual(total, 20.0)
        self.assertEqual([c["qty"] for c in calls], [12.0, 8.0])
        self.assertIn("Keluar proses persiapan", calls[0]["keterangan"] or "")
        self.assertIn("adjustment tidak ada sisa", (calls[1]["keterangan"] or "").lower())
        update_sql, update_params = cur.execute.call_args.args
        self.assertIn("yl_consumed=1", update_sql)
        self.assertEqual(update_params, (20.0, 7))

    def test_consume_is_idempotent_when_already_out(self):
        cur = MagicMock()
        total = _consume_yl_for_ky_session(
            cur,
            _ky(yl_consumed=1, qty_consumed=12.0),
            {"kode_wip": "WIP-99"},
        )
        self.assertEqual(total, 12.0)
        cur.execute.assert_not_called()


if __name__ == "__main__":
    unittest.main()
