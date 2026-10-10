import itertools
import math
import unittest

from _loader import load_solution

Solution = load_solution('62-unique-paths.py').Solution


def brute_force(m: int, n: int) -> int:
    """Independent full-grid DP (the closed form is checked separately)."""
    grid = [[1] * n for _ in range(m)]
    for i in range(1, m):
        for j in range(1, n):
            grid[i][j] = grid[i - 1][j] + grid[i][j - 1]
    return grid[m - 1][n - 1]


class UniquePathsTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().uniquePaths

    def test_official_examples(self):
        self.assertEqual(self.solve(3, 7), 28)
        self.assertEqual(self.solve(3, 2), 3)

    def test_single_row_or_column(self):
        self.assertEqual(self.solve(1, 1), 1)
        self.assertEqual(self.solve(1, 10), 1)
        self.assertEqual(self.solve(10, 1), 1)

    def test_matches_the_binomial_coefficient(self):
        for m in range(1, 21):
            for n in range(1, 21):
                with self.subTest(m=m, n=n):
                    self.assertEqual(self.solve(m, n), math.comb(m + n - 2, m - 1))

    def test_maximum_size(self):
        self.assertEqual(self.solve(100, 100), math.comb(198, 99))

    def test_exhaustive_small_grids(self):
        for m in range(1, 9):
            for n in range(1, 9):
                with self.subTest(m=m, n=n):
                    self.assertEqual(self.solve(m, n), brute_force(m, n))

    def test_all_grid_shapes_up_to_the_limit(self):
        for m, n in itertools.product([1, 2, 50, 99, 100], repeat=2):
            with self.subTest(m=m, n=n):
                self.assertEqual(self.solve(m, n), brute_force(m, n))


if __name__ == '__main__':
    unittest.main()
