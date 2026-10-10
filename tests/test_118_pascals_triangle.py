"""Tests for 118. Pascal's Triangle.

Oracles:
  - ``comb_oracle``: row i entry j is the binomial coefficient C(i, j), computed
    by CPython's exact-integer ``math.comb``. It shares no recurrence with the
    solution's neighbour addition.
  - row identities: length, symmetry, the 1s at both ends and sum(row i) = 2^i.
    These check properties of the output rather than agreement with a second
    implementation.

Exhaustive sweep: every allowed ``numRows`` from 1 to 30, plus the constraint
maximum as a dedicated case.
"""

import math
import unittest

from _loader import load_solution

Solution = load_solution('118-pascals-triangle.py').Solution

MAX_ROWS = 30


def comb_oracle(num_rows):
    """The triangle built from binomial coefficients."""
    return [[math.comb(row, column) for column in range(row + 1)]
            for row in range(num_rows)]


class PascalsTriangleTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().generate

    def test_official_examples(self):
        self.assertEqual(self.solve(5), [
            [1],
            [1, 1],
            [1, 2, 1],
            [1, 3, 3, 1],
            [1, 4, 6, 4, 1],
        ])
        self.assertEqual(self.solve(1), [[1]])

    def test_smallest_allowed_inputs(self):
        self.assertEqual(self.solve(1), comb_oracle(1))
        self.assertEqual(self.solve(2), [[1], [1, 1]])
        self.assertEqual(self.solve(3), [[1], [1, 1], [1, 2, 1]])

    def test_exhaustive_over_every_allowed_num_rows(self):
        for num_rows in range(1, MAX_ROWS + 1):
            with self.subTest(numRows=num_rows):
                self.assertEqual(self.solve(num_rows), comb_oracle(num_rows))

    def test_each_edge_of_every_deepened_row(self):
        # The solution appends the trailing 1 separately from the leading one,
        # so the edges are checked for every allowed size rather than inferred.
        for num_rows in range(1, MAX_ROWS + 1):
            triangle = self.solve(num_rows)
            for index, row in enumerate(triangle):
                with self.subTest(numRows=num_rows, row=index):
                    self.assertEqual(len(row), index + 1)
                    self.assertEqual(row[0], 1)
                    self.assertEqual(row[-1], 1)
                    self.assertEqual(row, row[::-1])
                    self.assertEqual(sum(row), 2 ** index)

    def test_neighbour_sum_holds_in_the_output(self):
        triangle = self.solve(MAX_ROWS)
        for index in range(1, MAX_ROWS):
            previous, row = triangle[index - 1], triangle[index]
            for column in range(1, len(row) - 1):
                with self.subTest(row=index, column=column):
                    self.assertEqual(row[column], previous[column - 1] + previous[column])

    def test_rows_are_independent_lists(self):
        triangle = self.solve(6)
        triangle[1][0] = 99
        self.assertEqual(triangle[2], [1, 2, 1])
        self.assertEqual(self.solve(6)[1], [1, 1])

    def test_constraint_sized(self):
        triangle = self.solve(MAX_ROWS)
        self.assertEqual(triangle, comb_oracle(MAX_ROWS))
        # Row 30 (1-based) is row index 29, so its middle pair is C(29, 14)
        # and C(29, 15), both 77_558_760.
        self.assertEqual(triangle[-1][14], math.comb(29, 14))
        self.assertEqual(triangle[-1][15], math.comb(29, 15))
        self.assertEqual(triangle[-1][15], 77_558_760)
        self.assertEqual(sum(sum(row) for row in triangle), 2 ** MAX_ROWS - 1)
        self.assertEqual(len(triangle[-1]), 30)


if __name__ == '__main__':
    unittest.main()
