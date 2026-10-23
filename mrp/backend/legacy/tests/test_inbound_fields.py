"""Harga dan supplier pada penerimaan, plus kolom baris YL."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from inbound_fields import (  # noqa: E402
    KIMIA_IN_SQL,
    MATERIAL_LAIN_IN_SQL,
    RP_IN_SQL,
    YL_UPSERT_SQL,
    commercial_from_body,
    yl_upsert_params,
)


class InboundCommercialTests(unittest.TestCase):
    def test_empty_supplier_and_price_are_allowed(self):
        commercial, err = commercial_from_body({})
        self.assertIsNone(err)
        self.assertEqual(commercial, {"supplier_name": None, "unit_price": None})

    def test_negative_price_rejected(self):
        commercial, err = commercial_from_body({"supplier_name": "PT A", "unit_price": -1})
        self.assertIsNone(commercial)
        self.assertIn("negatif", err)

    def test_stock_inserts_store_supplier_and_price(self):
        for sql in (KIMIA_IN_SQL, RP_IN_SQL, MATERIAL_LAIN_IN_SQL):
            self.assertIn("supplier_name", sql)
            self.assertIn("unit_price", sql)

    def test_palet_yl_stores_supplier_price_shape_scale_and_erp_id(self):
        params = yl_upsert_params(
            {
                "kode_yl": "MCL-2EP-102",
                "thickness": "1.02",
                "warna": "LIGHT BROWN",
                "qty": 4,
                "bentuk_kulit": "Utuh",
                "skala": "A",
                "unit_price": "12.5",
                "erp_material_id": 609,
            },
            kode_palet="KY-1",
            supplier_name="PT Kulit",
        )
        self.assertIn("supplier_name", YL_UPSERT_SQL)
        self.assertIn("bentuk_kulit", YL_UPSERT_SQL)
        self.assertIn("skala", YL_UPSERT_SQL)
        self.assertIn("erp_material_id", YL_UPSERT_SQL)
        self.assertEqual(params[0], "MCL-2EP-102")
        self.assertEqual(params[1], "KY-1")
        self.assertEqual(params[5], "PT Kulit")
        self.assertEqual(params[6], 12.5)
        self.assertEqual(params[7], "Utuh")
        self.assertEqual(params[8], "A")
        self.assertEqual(params[9], 609)


if __name__ == "__main__":
    unittest.main()
