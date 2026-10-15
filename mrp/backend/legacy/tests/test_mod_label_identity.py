"""Identitas kulit pada label reject Gudang MOD."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mod_label import _mod_label_identity  # noqa: E402


class ModLabelIdentityTests(unittest.TestCase):
    def test_rencana_supplies_material_backer_and_thickness(self):
        cur = MagicMock()
        got = _mod_label_identity(
            cur,
            {
                "rencana_item_id": 18,
                "rencana_material_name": "SPLIT SUEDE",
                "rencana_backer": "NAVY",
                "rencana_thickness": "1.2-1.4",
                "kode_palet": "KY-1",
                "kode_yl": "YL-1",
            },
        )
        self.assertEqual(
            got,
            {
                "material_name": "SPLIT SUEDE",
                "backer": "NAVY",
                "thickness": "1.2-1.4",
            },
        )
        cur.execute.assert_not_called()

    def test_missing_rencana_uses_yl_stock(self):
        cur = MagicMock()
        cur.fetchone.return_value = {"thickness": "1.0", "warna": "HITAM"}
        got = _mod_label_identity(
            cur,
            {
                "rencana_item_id": None,
                "kode_palet": "KY-1",
                "kode_yl": "YL-1",
            },
        )
        self.assertEqual(got["material_name"], "")
        self.assertEqual(got["thickness"], "1.0")
        self.assertEqual(got["backer"], "HITAM")
        sql = cur.execute.call_args[0][0]
        self.assertIn("tbl_yl", sql)
        self.assertNotIn("tbl_yl_movement", sql)

    def test_missing_yl_row_falls_back_to_movement(self):
        cur = MagicMock()
        cur.fetchone.side_effect = [None, {"thickness": "1.2", "warna": "COKELAT"}]
        got = _mod_label_identity(
            cur,
            {"rencana_item_id": None, "kode_palet": "KY-9", "kode_yl": "YL-9"},
        )
        self.assertEqual(got["thickness"], "1.2")
        self.assertEqual(got["backer"], "COKELAT")
        self.assertEqual(cur.execute.call_count, 2)
        history_sql = cur.execute.call_args_list[1][0][0]
        self.assertIn("tbl_yl_movement", history_sql)


if __name__ == "__main__":
    unittest.main()
