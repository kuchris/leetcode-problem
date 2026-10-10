"""Tests for 77. Combinations.

Oracle: itertools.combinations over range(1, n + 1), which enumerates the
k-subsets without any backtracking of its own.
"""

import itertools
import math
import unittest

from _loader import load_solution

Solution = load_solution('77-combinations.py').Solution


def brute_force(n: int, k: int) -> set[tuple[int, ...]]:
    """The k-subsets of {1..n}, straight from itertools."""
    return set(itertools.combinations(range(1, n + 1), k))


def as_set(rows: list[list[int]]) -> set[tuple[int, ...]]:
    return {tuple(row) for row in rows}


class CombinationsTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().combine

    def test_official_examples(self):
        self.assertEqual(
            sorted(self.solve(4, 2)),
            [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]],
        )
        self.assertEqual(self.solve(1, 1), [[1]])

    def test_k_equals_n(self):
        self.assertEqual(self.solve(1, 1), [[1]])
        self.assertEqual(self.solve(5, 5), [[1, 2, 3, 4, 5]])
        self.assertEqual(self.solve(20, 20), [list(range(1, 21))])

    def test_k_equals_one(self):
        self.assertEqual(self.solve(5, 1), [[1], [2], [3], [4], [5]])
        self.assertEqual(self.solve(1, 1), [[1]])

    def test_smallest_and_largest_n(self):
        self.assertEqual(self.solve(1, 1), [[1]])
        self.assertEqual(len(self.solve(20, 19)), 20)

    def test_count_matches_binomial_coefficient(self):
        for n in range(1, 13):
            for k in range(1, n + 1):
                with self.subTest(n=n, k=k):
                    self.assertEqual(len(self.solve(n, k)), math.comb(n, k))

    def test_every_combination_is_valid_and_unique(self):
        for k in range(1, 9):
            rows = self.solve(8, k)
            with self.subTest(k=k):
                self.assertEqual(len(rows), len(as_set(rows)))
                for row in rows:
                    self.assertEqual(len(row), k)
                    self.assertEqual(sorted(row), row)
                    self.assertTrue(all(1 <= value <= 8 for value in row))

    def test_exhaustive_small_cases(self):
        for n in range(1, 9):
            for k in range(1, n + 1):
                with self.subTest(n=n, k=k):
                    self.assertEqual(as_set(self.solve(n, k)), brute_force(n, k))

    def test_mid_sized_case_matches_oracle_exactly(self):
        rows = self.solve(14, 7)
        self.assertEqual(len(rows), math.comb(14, 7))
        self.assertEqual(as_set(rows), brute_force(14, 7))

    def test_constraint_sized(self):
        # n = 20, k = 10 is the largest output the constraints allow.
        rows = self.solve(20, 10)
        self.assertEqual(len(rows), math.comb(20, 10))
        self.assertEqual(len(as_set(rows)), math.comb(20, 10))
        for row in (rows[0], rows[len(rows) // 2], rows[-1]):
            self.assertEqual(len(row), 10)
            self.assertEqual(sorted(row), row)
            self.assertTrue(all(1 <= value <= 20 for value in row))
        self.assertEqual(rows[0], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.assertEqual(rows[-1], [11, 12, 13, 14, 15, 16, 17, 18, 19, 20])


if __name__ == '__main__':
    unittest.main()
