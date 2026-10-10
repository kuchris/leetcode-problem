"""Tests for 85. Maximal Rectangle.

Oracle: for every pair of rows (top, bottom) keep the columns that are all '1'
between them and take the longest run of such columns; that run times the row
count is the best rectangle with those two rows as its vertical borders. It is
the O(rows^2 * cols) row-pair algorithm, not the per-row histogram reduction
under test, so it shares no code with the solution.
"""

import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('85-maximal-rectangle.py').Solution


def brute_force(matrix: list[list[str]]) -> int:
    rows, cols = len(matrix), len(matrix[0])
    best = 0
    for top in range(rows):
        all_ones = [True] * cols
        for bottom in range(top, rows):
            for c in range(cols):
                if matrix[bottom][c] != '1':
                    all_ones[c] = False
            run = 0
            for c in range(cols):
                run = run + 1 if all_ones[c] else 0
                area = run * (bottom - top + 1)
                if area > best:
                    best = area
    return best


def board(rows: int, cols: int, filled: str = '0') -> list[list[str]]:
    return [[filled] * cols for _ in range(rows)]


OFFICIAL = [["1", "0", "1", "0", "0"],
            ["1", "0", "1", "1", "1"],
            ["1", "1", "1", "1", "1"],
            ["1", "0", "0", "1", "0"]]

SHAPES = [(1, 1), (1, 2), (1, 3), (2, 2), (2, 3), (2, 4), (3, 3)]


class MaximalRectangleTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().maximalRectangle

    def test_official_examples(self):
        self.assertEqual(self.solve([row[:] for row in OFFICIAL]), 6)
        self.assertEqual(self.solve([["0"]]), 0)
        self.assertEqual(self.solve([["1"]]), 1)

    def test_single_row_and_column(self):
        self.assertEqual(self.solve([["1", "1", "1"]]), 3)
        self.assertEqual(self.solve([["1", "0", "1", "1"]]), 2)
        self.assertEqual(self.solve([["1"], ["1"], ["0"], ["1"]]), 2)
        self.assertEqual(self.solve([["0"], ["0"]]), 0)

    def test_all_ones(self):
        self.assertEqual(self.solve(board(4, 6, '1')), 24)
        self.assertEqual(self.solve(board(1, 1, '1')), 1)

    def test_all_zeros(self):
        self.assertEqual(self.solve(board(5, 5, '0')), 0)

    def test_single_cell_in_a_sea_of_zeros(self):
        matrix = board(4, 4, '0')
        matrix[1][2] = '1'
        self.assertEqual(self.solve(matrix), 1)

    def test_wide_short_beats_tall_narrow(self):
        matrix = board(5, 5, '0')
        for r in range(5):
            matrix[r][0] = '1'
        for c in range(5):
            matrix[0][c] = '1'
        self.assertEqual(self.solve(matrix), 5)

    def test_hole_inside_a_block(self):
        matrix = board(3, 3, '1')
        matrix[1][1] = '0'
        self.assertEqual(self.solve(matrix), 3)

    def test_exhaustive_small_cases(self):
        for rows, cols in SHAPES:
            for flat in itertools.product('01', repeat=rows * cols):
                matrix = [list(flat[r * cols:(r + 1) * cols]) for r in range(rows)]
                with self.subTest(matrix=matrix):
                    self.assertEqual(self.solve([row[:] for row in matrix]), brute_force(matrix))

    def test_randomised_cases(self):
        rng = random.Random(850)
        for _ in range(40):
            rows, cols = rng.randint(1, 12), rng.randint(1, 12)
            matrix = [[rng.choice('01') for _ in range(cols)] for _ in range(rows)]
            with self.subTest(rows=rows, cols=cols):
                self.assertEqual(self.solve([row[:] for row in matrix]), brute_force(matrix))

    def test_randomised_dense_cases(self):
        # Mostly '1' with a few holes, which stresses the histogram reduction.
        rng = random.Random(851)
        for _ in range(20):
            rows, cols = 20, 20
            matrix = [['1' if rng.random() > 0.15 else '0' for _ in range(cols)]
                      for _ in range(rows)]
            with self.subTest(seed=851):
                self.assertEqual(self.solve([row[:] for row in matrix]), brute_force(matrix))

    def test_constraint_sized(self):
        rows = cols = 200

        self.assertEqual(self.solve(board(rows, cols, '1')), rows * cols)
        self.assertEqual(self.solve(board(rows, cols, '0')), 0)

        # A planted 37 x 50 block of ones inside a zero field.
        matrix = board(rows, cols)
        for r in range(10, 47):
            for c in range(20, 70):
                matrix[r][c] = '1'
        self.assertEqual(self.solve([row[:] for row in matrix]), 37 * 50)
        self.assertEqual(brute_force(matrix), 37 * 50)

        # A full first row makes the top strip 200 wide but only 1 tall.
        strip = board(rows, cols)
        strip[0] = ['1'] * cols
        self.assertEqual(self.solve([row[:] for row in strip]), cols)


if __name__ == '__main__':
    unittest.main()
