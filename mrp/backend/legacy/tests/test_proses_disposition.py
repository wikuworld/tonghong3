"""Alasan baris Reject/Return yang sisa ukurnya habis."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from proses_disposition import line_block_reason  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
