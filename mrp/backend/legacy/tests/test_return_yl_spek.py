"""Sisa KY ke palet harus mempertahankan thickness/warna setelah OUT penuh."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import _return_yl_to_palet  # noqa: E402


class ReturnYlSpekTests(unittest.TestCase):
    def test_reinsert_uses_movement_history_when_row_deleted(self):
        cur = MagicMock()
        # 1) SELECT tbl_yl — tidak ada baris
        # 2) INSERT movement IN
        # 3) INSERT tbl_yl
        cur.fetchone.side_effect = [
            None,
            {"thickness": "1.2", "warna": "HITAM"},
        ]
        inserted_yl = []

        def capture_execute(sql, params=None):
            if params and "INSERT INTO tbl_yl" in sql:
                inserted_yl.append(params)

        cur.execute.side_effect = capture_execute

        qty = _return_yl_to_palet(cur, "PAL-1", "YL-1", 50.0, keterangan="test")
        self.assertEqual(qty, 50.0)
        self.assertEqual(len(inserted_yl), 1)
        _kode_yl, _palet, thickness, warna, q = inserted_yl[0]
        self.assertEqual(thickness, "1.2")
        self.assertEqual(warna, "HITAM")
        self.assertEqual(q, 50.0)


if __name__ == "__main__":
    unittest.main()
