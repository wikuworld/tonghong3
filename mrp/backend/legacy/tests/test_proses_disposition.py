"""Alasan baris Reject/Return yang sisa ukurnya habis."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from proses_disposition import (  # noqa: E402
    line_block_reason,
    parse_ukur_sizes,
    qty_from_ukur_sizes,
)


class LineBlockReasonTests(unittest.TestCase):
    def test_sisa_masih_ada(self):
        self.assertIsNone(
            line_block_reason(measured=121, returned=0, rejected=0, remaining=121)
        )

    def test_sudah_diretur(self):
        self.assertEqual(
            line_block_reason(measured=450, returned=450, rejected=0, remaining=0),
            "sudah diretur",
        )

    def test_sudah_direject(self):
        self.assertEqual(
            line_block_reason(measured=450, returned=0, rejected=450, remaining=0),
            "sudah direject",
        )

    def test_keduanya(self):
        self.assertEqual(
            line_block_reason(measured=100, returned=40, rejected=60, remaining=0),
            "sudah diretur dan sudah direject",
        )

    def test_belum_diukur(self):
        self.assertEqual(
            line_block_reason(measured=0, returned=0, rejected=0, remaining=0),
            "belum ada hasil ukur",
        )


class ParseUkurSizesTests(unittest.TestCase):
    def test_ukur_sizes_list(self):
        self.assertEqual(parse_ukur_sizes({"ukur_sizes": [12.5, 10]}), [12.5, 10.0])

    def test_ukur_rows_objects(self):
        self.assertEqual(
            parse_ukur_sizes({"ukur_rows": [{"size_val": 5}, {"size": 7.2}]}),
            [5.0, 7.2],
        )

    def test_skips_non_positive(self):
        self.assertEqual(parse_ukur_sizes({"ukur_sizes": [0, -1, 3]}), [3.0])

    def test_empty_when_missing(self):
        self.assertEqual(parse_ukur_sizes({}), [])
        self.assertEqual(parse_ukur_sizes(None), [])

    def test_qty_from_ukur_sizes(self):
        total, lembar = qty_from_ukur_sizes([10, 20.5])
        self.assertEqual(total, 30.5)
        self.assertEqual(lembar, 2)
        self.assertEqual(qty_from_ukur_sizes([]), (0.0, 0))


if __name__ == "__main__":
    unittest.main()
