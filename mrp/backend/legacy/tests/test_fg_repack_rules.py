import unittest

from fg_repack_rules import validate_repack_lines


class RepackRulesTest(unittest.TestCase):
    def test_whole_repack_matches(self):
        err, parsed = validate_repack_lines([{"lembar": 3, "ukuran": 120.5}], 3, 120.5)
        self.assertIsNone(err)
        self.assertEqual(parsed, [{"lembar": 3, "ukuran": 120.5}])

    def test_split_must_sum_to_source(self):
        err, parsed = validate_repack_lines(
            [{"lembar": 1, "ukuran": 40}, {"lembar": 2, "ukuran": 80.5}],
            3,
            120.5,
        )
        self.assertIsNone(err)
        self.assertEqual(len(parsed), 2)

    def test_ukuran_tolerance(self):
        err, _parsed = validate_repack_lines([{"lembar": 1, "ukuran": 10.01}], 1, 10)
        self.assertIsNone(err)
        err, _parsed = validate_repack_lines([{"lembar": 1, "ukuran": 10.02}], 1, 10)
        self.assertIn("ukuran", err)

    def test_lembar_mismatch(self):
        err, parsed = validate_repack_lines([{"lembar": 2, "ukuran": 10}], 3, 10)
        self.assertIsNone(parsed)
        self.assertIn("lembar", err)

    def test_empty(self):
        err, parsed = validate_repack_lines([], 1, 1)
        self.assertIsNone(parsed)
        self.assertTrue(err)


if __name__ == "__main__":
    unittest.main()
