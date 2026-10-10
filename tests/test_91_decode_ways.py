"""Tests for 91. Decode Ways.

Two independent oracles:

  - `brute_force` walks the string from the left and enumerates every legal
    grouping (single digit, or a two-digit code 10..26) -- no DP table.
  - `suffix_dp` is a memoised recursion over suffixes, i.e. the opposite
    direction and the opposite evaluation order from the prefix rolling DP under
    test; it is what makes the length-100 cases checkable.

The all-ones string also has the closed form Fib(n+1), computed here by a plain
iterative Fibonacci loop.
"""

import itertools
import random
import unittest
from functools import lru_cache

from _loader import load_solution

Solution = load_solution('91-decode-ways.py').Solution


def brute_force(s: str) -> int:
    """Enumerate every valid grouping of the digits."""
    def count(i: int) -> int:
        if i == len(s):
            return 1
        if s[i] == '0':
            return 0
        total = count(i + 1)
        if i + 1 < len(s) and int(s[i:i + 2]) <= 26:
            total += count(i + 2)
        return total

    return count(0)


def suffix_dp(s: str) -> int:
    """Memoised count over the suffixes of s."""
    n = len(s)

    @lru_cache(maxsize=None)
    def ways(i: int) -> int:
        if i == n:
            return 1
        if s[i] == '0':
            return 0
        total = ways(i + 1)
        if i + 2 <= n and s[i:i + 2] <= '26':
            total += ways(i + 2)
        return total

    return ways(0)


def fibonacci(index: int) -> int:
    """fib(1) = fib(2) = 1, computed iteratively."""
    a, b = 1, 1
    for _ in range(index - 1):
        a, b = b, a + b
    return a


class DecodeWaysTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().numDecodings

    def test_official_examples(self):
        self.assertEqual(self.solve('12'), 2)
        self.assertEqual(self.solve('226'), 3)
        self.assertEqual(self.solve('06'), 0)

    def test_single_digit(self):
        self.assertEqual(self.solve('1'), 1)
        self.assertEqual(self.solve('9'), 1)
        self.assertEqual(self.solve('0'), 0)

    def test_two_digit_boundaries(self):
        self.assertEqual(self.solve('10'), 1)
        self.assertEqual(self.solve('26'), 2)
        self.assertEqual(self.solve('27'), 1)
        self.assertEqual(self.solve('20'), 1)
        self.assertEqual(self.solve('30'), 0)
        self.assertEqual(self.solve('00'), 0)
        self.assertEqual(self.solve('09'), 0)

    def test_leading_and_embedded_zeros(self):
        for s in ('01', '010', '100', '1001', '101', '110', '10001'):
            with self.subTest(s=s):
                self.assertEqual(self.solve(s), brute_force(s))

    def test_known_groups(self):
        self.assertEqual(self.solve('11106'), 2)
        self.assertEqual(self.solve('1111'), 5)
        self.assertEqual(self.solve('666'), 1)

    def test_impossible_strings(self):
        self.assertEqual(self.solve('0'), 0)
        self.assertEqual(self.solve('06'), 0)
        self.assertEqual(self.solve('100'), 0)
        self.assertEqual(self.solve('0' * 5), 0)

    def test_exhaustive_small_cases_with_zeros(self):
        for length in range(1, 6):
            for chars in itertools.product('01267', repeat=length):
                s = ''.join(chars)
                with self.subTest(s=s):
                    self.assertEqual(self.solve(s), brute_force(s))

    def test_exhaustive_fibonacci_cases(self):
        # Every string of 1s and 2s: no zero, so the count is Fibonacci-like.
        for length in range(1, 9):
            for chars in itertools.product('12', repeat=length):
                s = ''.join(chars)
                with self.subTest(s=s):
                    self.assertEqual(self.solve(s), brute_force(s))

    def test_randomised_cases(self):
        rng = random.Random(910)
        for _ in range(300):
            s = ''.join(rng.choice('0123456789') for _ in range(rng.randint(1, 12)))
            with self.subTest(s=s):
                self.assertEqual(self.solve(s), brute_force(s))

    def test_constraint_sized(self):
        # 100 digits is the constraint maximum.
        self.assertEqual(self.solve('1' * 100), fibonacci(101))
        self.assertEqual(self.solve('0' * 100), 0)
        self.assertEqual(self.solve('10' * 50), 1)
        self.assertEqual(self.solve('27' * 50), 1)
        self.assertEqual(self.solve('6' * 100), 1)
        self.assertEqual(self.solve('20' * 50), 1)
        self.assertEqual(self.solve('11' * 50), suffix_dp('11' * 50))

    def test_constraint_sized_random_strings(self):
        rng = random.Random(911)
        for _ in range(100):
            s = ''.join(rng.choice('0123456789') for _ in range(100))
            with self.subTest(s=s):
                self.assertEqual(self.solve(s), suffix_dp(s))

    def test_constraint_sized_ones_and_twos(self):
        rng = random.Random(912)
        for _ in range(50):
            s = ''.join(rng.choice('12') for _ in range(100))
            with self.subTest(s=s):
                self.assertEqual(self.solve(s), suffix_dp(s))


if __name__ == '__main__':
    unittest.main()
