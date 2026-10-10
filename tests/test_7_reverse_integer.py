import unittest

from _loader import load_solution

Solution = load_solution('7-reverse-integer.py').Solution

INT_MIN = -(2 ** 31)
INT_MAX = 2 ** 31 - 1


def brute_force(x: int) -> int:
    """Reverse the decimal text, then apply the 32-bit range rule."""
    sign = -1 if x < 0 else 1
    digits = str(abs(x))[::-1]
    value = sign * int(digits)
    return value if INT_MIN <= value <= INT_MAX else 0


class ReverseIntegerTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().reverse

    def test_official_examples(self):
        self.assertEqual(self.solve(123), 321)
        self.assertEqual(self.solve(-123), -321)
        self.assertEqual(self.solve(120), 21)

    def test_zero(self):
        self.assertEqual(self.solve(0), 0)

    def test_trailing_zeros_are_dropped(self):
        self.assertEqual(self.solve(100), 1)
        self.assertEqual(self.solve(-1000), -1)

    def test_overflow_returns_zero(self):
        # 7463847412 and 8463847412 both exceed INT_MAX.
        self.assertEqual(self.solve(INT_MAX), 0)
        self.assertEqual(self.solve(INT_MIN), 0)
        self.assertEqual(self.solve(1534236469), 0)
        self.assertEqual(self.solve(1000000003), 0)

    def test_negative_value_that_stays_in_range(self):
        self.assertEqual(self.solve(-2147483412), -2143847412)

    def test_exhaustive_range_and_boundaries(self):
        cases = list(range(-1200, 1201)) + [INT_MIN, INT_MIN + 1, INT_MAX, INT_MAX - 1]
        for x in cases:
            with self.subTest(x=x):
                self.assertEqual(self.solve(x), brute_force(x))


if __name__ == '__main__':
    unittest.main()
