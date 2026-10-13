"""Tests for 172. Factorial Trailing Zeroes.

Three independent oracles, none of which follows the solution's `power *= 5`
loop:

  - ``legendre_oracle``: the same Legendre sum, but over a fixed precomputed
    table of powers of five rather than a growing variable;
  - ``factorial_brute``: the definition -- actually build n! with
    ``math.factorial`` and divide by ten until it stops being divisible (only
    feasible for small n, which is exactly where it is the ground truth);
  - ``factor_count_oracle``: elementary prime-factor counting. Every trailing
    zero needs a 2 and a 5, so the answer is min(number of factors 2 in n!,
    number of factors 5 in n!). It factors every integer up to n and uses no
    formula at all.

A structural property is checked exhaustively as well: zeroes(n) - zeroes(n - 1)
must equal the exponent of 5 in n, which follows from the definition and pins
every step of the sequence rather than only the test points.
"""

import math
import unittest

from _loader import load_solution

Solution = load_solution('172-factorial-trailing-zeroes.py').Solution

MAX_N = 10_000
POWERS_OF_FIVE = [5 ** exponent for exponent in range(1, 20)]


def legendre_oracle(n: int) -> int:
    return sum(n // power for power in POWERS_OF_FIVE if power <= n)


def factorial_brute(n: int) -> int:
    value = math.factorial(n)
    zeroes = 0
    while value % 10 == 0:
        value //= 10
        zeroes += 1
    return zeroes


def factor_count_oracle(n: int) -> int:
    fives = twos = 0
    for value in range(2, n + 1):
        while value % 5 == 0:
            fives += 1
            value //= 5
        while value % 2 == 0:
            twos += 1
            value //= 2
    return min(fives, twos)


def exponent_of_five(value: int) -> int:
    exponent = 0
    while value % 5 == 0:
        value //= 5
        exponent += 1
    return exponent


class FactorialTrailingZeroesTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().trailingZeroes

    def check(self, n):
        produced = self.solve(n)
        self.assertEqual(produced, legendre_oracle(n), f'n={n}')
        return produced

    def test_official_examples(self):
        self.assertEqual(self.solve(3), 0)
        self.assertEqual(self.solve(5), 1)
        self.assertEqual(self.solve(0), 0)
        self.assertEqual(self.check(3), 0)
        self.assertEqual(self.check(5), 1)
        self.assertEqual(self.check(0), 0)

    def test_small_values_against_the_actual_factorial(self):
        for n in range(0, 501):
            with self.subTest(n=n):
                self.assertEqual(self.solve(n), factorial_brute(n))

    def test_powers_of_five_boundaries(self):
        expected = {
            0: 0, 1: 0, 4: 0, 5: 1, 9: 1, 10: 2, 24: 4, 25: 6,
            26: 6, 124: 28, 125: 31, 126: 31, 624: 152, 625: 156,
            626: 156, 3124: 776, 3125: 781, 3126: 781, 9999: 2495,
            10000: 2499,
        }
        for n, zeroes in expected.items():
            with self.subTest(n=n):
                self.assertEqual(self.solve(n), zeroes)
                self.assertEqual(self.solve(n), legendre_oracle(n))

    def test_constraint_sized(self):
        # n = 10^4 is the constraint maximum; its factorial has 35,660 digits,
        # so this must be a counting solution and not a factorial one.
        self.assertEqual(self.solve(MAX_N), 2499)
        self.assertEqual(self.solve(MAX_N), legendre_oracle(MAX_N))
        self.assertEqual(2000 + 400 + 80 + 16 + 3, 2499)
        self.assertEqual(self.solve(MAX_N - 1), legendre_oracle(MAX_N - 1))

    def test_exhaustive_small_cases(self):
        for n in range(0, 1001):
            with self.subTest(n=n):
                self.assertEqual(self.solve(n), legendre_oracle(n))

    def test_exhaustive_across_the_whole_constraint(self):
        for n in range(0, MAX_N + 1):
            with self.subTest(n=n):
                self.assertEqual(self.solve(n), legendre_oracle(n))

    def test_increments_are_the_exponent_of_five(self):
        # zeroes(n) - zeroes(n - 1) == v5(n): every step of the sequence is
        # pinned, not only the sampled values.
        previous = self.solve(0)
        for n in range(1, MAX_N + 1):
            current = self.solve(n)
            with self.subTest(n=n):
                self.assertEqual(current - previous, exponent_of_five(n))
            previous = current

    def test_factor_count_oracle(self):
        checks = list(range(0, 301)) + [400, 500, 625, 1000, 2000, 3125, 5000, 10_000]
        for n in checks:
            with self.subTest(n=n):
                self.assertEqual(self.solve(n), factor_count_oracle(n))

    def test_monotone(self):
        previous = -1
        for n in range(0, MAX_N + 1, 7):
            current = self.solve(n)
            with self.subTest(n=n):
                self.assertGreaterEqual(current, previous)
            previous = current


if __name__ == '__main__':
    unittest.main()
