import random
import unittest

from _loader import load_solution

Solution = load_solution('50-powx-n.py').Solution


class PowXNTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().myPow

    def assert_close(self, result: float, expected: float):
        if expected == 0:
            self.assertEqual(result, 0.0)
        else:
            self.assertAlmostEqual(result / expected, 1.0, places=9)

    def test_official_examples(self):
        self.assert_close(self.solve(2.0, 10), 1024.0)
        self.assert_close(self.solve(2.1, 3), 9.261)
        self.assert_close(self.solve(2.0, -2), 0.25)

    def test_exponent_zero(self):
        self.assertEqual(self.solve(2.0, 0), 1.0)
        self.assertEqual(self.solve(-3.5, 0), 1.0)

    def test_base_one_and_minus_one(self):
        self.assertEqual(self.solve(1.0, 10 ** 9), 1.0)
        self.assertEqual(self.solve(1.0, -(10 ** 9)), 1.0)
        self.assertEqual(self.solve(-1.0, 10 ** 9), 1.0)
        self.assertEqual(self.solve(-1.0, 10 ** 9 + 1), -1.0)

    def test_negative_base_parity(self):
        self.assert_close(self.solve(-2.0, 3), -8.0)
        self.assert_close(self.solve(-2.0, 4), 16.0)

    def test_fractional_base(self):
        self.assert_close(self.solve(0.5, 3), 0.125)
        self.assert_close(self.solve(0.5, -3), 8.0)

    def test_extreme_exponents(self):
        # 1 is unaffected by the exponent magnitude, so this stays exact.
        self.assertEqual(self.solve(1.0, 2 ** 31 - 1), 1.0)
        self.assertEqual(self.solve(1.0, -(2 ** 31)), 1.0)
        # Small bases underflow to zero on both sides.
        self.assertEqual(self.solve(2.0, -(2 ** 31)), 0.0)

    def test_exhaustive_integer_exponents(self):
        for base in (0.5, 1.0, 1.5, 2.0, 2.5, -1.5, -2.0, 10.0):
            for exponent in range(-20, 21):
                with self.subTest(base=base, exponent=exponent):
                    self.assert_close(self.solve(base, exponent), base ** exponent)

    def test_randomised_cases(self):
        rng = random.Random(50)
        checked = 0
        for _ in range(300):
            base = rng.uniform(-100, 100)
            exponent = rng.randint(-(2 ** 31), 2 ** 31 - 1)
            try:
                expected = base ** exponent
            except OverflowError:
                # The true value leaves the documented range; not a valid input.
                continue
            if expected != 0 and not (1e-300 < abs(expected) < 1e300):
                continue
            with self.subTest(base=base, exponent=exponent):
                self.assert_close(self.solve(base, exponent), expected)
                checked += 1
        self.assertGreater(checked, 0, 'no randomised case survived the range guard')


if __name__ == '__main__':
    unittest.main()
