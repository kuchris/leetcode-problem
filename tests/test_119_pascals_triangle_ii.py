"""Tests for 119. Pascal's Triangle II.

Oracles:
  - ``comb_oracle``: row n is [C(n, k) for k in range(n + 1)] with CPython's
    exact ``math.comb``, so it never multiplies-and-divides the way the
    solution does.
  - ``addition_oracle``: the textbook "each entry is the sum of the two above"
    recurrence, a deliberately different algorithm from the closed-form
    multiplicative step in the solution.

Exhaustive sweep: every allowed ``rowIndex`` 0..33 against both oracles, then the
constraint maximum with its identities (sum = 2^n, symmetry, known middle value).
"""

import math
import unittest

from _loader import load_solution

Solution = load_solution('119-pascals-triangle-ii.py').Solution

MAX_INDEX = 33


def comb_oracle(row_index) -> list:
    return [math.comb(row_index, column) for column in range(row_index + 1)]


def addition_oracle(row_index) -> list:
    """Grow the row by the addition recurrence, padding with zeros at the ends."""
    row = [1]
    for _ in range(row_index):
        row = [above + below for above, below in zip([0] + row, row + [0])]
    return row


class PascalsTriangleIITests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().getRow

    def test_official_examples(self):
        self.assertEqual(self.solve(3), [1, 3, 3, 1])
        self.assertEqual(self.solve(0), [1])
        self.assertEqual(self.solve(1), [1, 1])

    def test_smallest_and_second_smallest_inputs(self):
        self.assertEqual(self.solve(0), comb_oracle(0))
        self.assertEqual(self.solve(2), [1, 2, 1])
        self.assertEqual(self.solve(2), addition_oracle(2))

    def test_exhaustive_over_every_allowed_row_index(self):
        for row_index in range(0, MAX_INDEX + 1):
            with self.subTest(rowIndex=row_index):
                self.assertEqual(self.solve(row_index), comb_oracle(row_index))
                self.assertEqual(self.solve(row_index), addition_oracle(row_index))

    def test_row_identities(self):
        for row_index in range(0, MAX_INDEX + 1):
            row = self.solve(row_index)
            with self.subTest(rowIndex=row_index):
                self.assertEqual(len(row), row_index + 1)
                self.assertEqual(row[0], 1)
                self.assertEqual(row[-1], 1)
                self.assertEqual(row, row[::-1])
                self.assertEqual(sum(row), 2 ** row_index)

    def test_division_in_the_multiplicative_step_is_exact(self):
        # The solution divides by k, so every intermediate product must be a
        # multiple of k; check the closed form directly for the largest row.
        row = self.solve(MAX_INDEX)
        for k in range(1, MAX_INDEX + 1):
            with self.subTest(k=k):
                self.assertEqual(row[k - 1] * (MAX_INDEX - k + 1) % k, 0)
                self.assertEqual(row[k], row[k - 1] * (MAX_INDEX - k + 1) // k)

    def test_returns_a_fresh_list(self):
        first = self.solve(4)
        first[0] = 99
        self.assertEqual(self.solve(4), [1, 4, 6, 4, 1])

    def test_constraint_sized(self):
        row = self.solve(MAX_INDEX)
        self.assertEqual(row, comb_oracle(MAX_INDEX))
        self.assertEqual(row, addition_oracle(MAX_INDEX))
        self.assertEqual(len(row), 34)
        self.assertEqual(row[16], 1_166_803_110)
        self.assertEqual(sum(row), 2 ** 33)
        self.assertEqual(sum(row), 8_589_934_592)


if __name__ == '__main__':
    unittest.main()
