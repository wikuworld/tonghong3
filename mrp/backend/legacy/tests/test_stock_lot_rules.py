import unittest

from stock_lot_rules import validate_lot_delete, validate_lot_update


class StockLotRulesTest(unittest.TestCase):
    def test_update_qty_above_issued(self):
        err = validate_lot_update(
            qty_new=8,
            issued=5,
            qty_book=10,
            qty_sisa_book=5,
            out_count=1,
            locked_changed=False,
        )
        self.assertIsNone(err)

    def test_update_qty_below_issued(self):
        err = validate_lot_update(
            qty_new=4,
            issued=5,
            qty_book=10,
            qty_sisa_book=5,
            out_count=1,
            locked_changed=False,
        )
        self.assertIn("lebih kecil", err)

    def test_update_mismatch_rejected(self):
        err = validate_lot_update(
            qty_new=10,
            issued=1,
            qty_book=10,
            qty_sisa_book=10,
            out_count=1,
            locked_changed=False,
        )
        self.assertIn("tidak cocok", err)

    def test_locked_fields_after_out(self):
        err = validate_lot_update(
            qty_new=10,
            issued=2,
            qty_book=10,
            qty_sisa_book=8,
            out_count=1,
            locked_changed=True,
        )
        self.assertIn("hanya qty", err)

    def test_delete_lapangan_and_out(self):
        self.assertIn("lapangan", validate_lot_delete(
            out_count=0, gudang="lapangan", has_sisa_note=False, has_usage=False,
        ))
        self.assertIn("keluar", validate_lot_delete(
            out_count=1, gudang="utama", has_sisa_note=False, has_usage=False,
        ))
        self.assertIsNone(validate_lot_delete(
            out_count=0, gudang="utama", has_sisa_note=False, has_usage=False,
        ))
        self.assertIsNone(validate_lot_delete(
            out_count=0, gudang=None, has_sisa_note=False, has_usage=False, block_lapangan=False,
        ))


if __name__ == "__main__":
    unittest.main()
