import random
import unittest

from _loader import load_solution

Solution = load_solution('29-divide-two-integers.py').Solution

INT_MIN = -(2 ** 31)
INT_MAX = 2 ** 31 - 1


def brute_force(dividend: int, divisor: int) -> int:
    """Truncating division computed from the magnitudes, then clamped."""
    if dividend == INT_MIN and divisor == -1:
        return INT_MAX
    quotient = abs(dividend) // abs(divisor)
    if (dividend < 0) != (divisor < 0):
        quotient = -quotient
    return max(INT_MIN, min(INT_MAX, quotient))


class DivideTwoIntegersTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().divide

    def test_official_examples(self):
        self.assertEqual(self.solve(10, 3), 3)
        self.assertEqual(self.solve(7, -3), -2)

    def test_truncates_toward_zero(self):
        self.assertEqual(self.solve(-7, 3), -2)
        self.assertEqual(self.solve(7, 3), 2)
        self.assertEqual(self.solve(-8, 3), -2)

    def test_zero_dividend(self):
        self.assertEqual(self.solve(0, 1), 0)
        self.assertEqual(self.solve(0, -5), 0)

    def test_divisor_of_one(self):
        self.assertEqual(self.solve(INT_MAX, 1), INT_MAX)
        self.assertEqual(self.solve(INT_MIN, 1), INT_MIN)

    def test_the_single_overflow_case_saturates(self):
        self.assertEqual(self.solve(INT_MIN, -1), INT_MAX)

    def test_boundary_division(self):
        self.assertEqual(self.solve(INT_MIN, 2), -1073741824)
        self.assertEqual(self.solve(INT_MIN, INT_MIN), 1)
        self.assertEqual(self.solve(INT_MAX, INT_MAX), 1)
        self.assertEqual(self.solve(INT_MAX, -1), -INT_MAX)

    def test_dividend_smaller_than_divisor(self):
        self.assertEqual(self.solve(1, 2), 0)
        self.assertEqual(self.solve(-1, 2), 0)

    def test_exhaustive_small_cases(self):
        for dividend in range(-60, 61):
            for divisor in range(-12, 13):
                if divisor == 0:
                    continue
                with self.subTest(dividend=dividend, divisor=divisor):
                    self.assertEqual(
                        self.solve(dividend, divisor), brute_force(dividend, divisor)
                    )

    def test_randomised_boundary_values(self):
        rng = random.Random(29)
        edges = [INT_MIN, INT_MIN + 1, -2, -1, 1, 2, INT_MAX - 1, INT_MAX]
        for _ in range(300):
            dividend = rng.choice(edges) if rng.random() < 0.5 else rng.randint(INT_MIN, INT_MAX)
            divisor = rng.choice(edges) if rng.random() < 0.5 else rng.randint(-1000, 1000)
            if divisor == 0:
                continue
            with self.subTest(dividend=dividend, divisor=divisor):
                self.assertEqual(
                    self.solve(dividend, divisor), brute_force(dividend, divisor)
                )


if __name__ == '__main__':
    unittest.main()
