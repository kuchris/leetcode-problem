import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('64-minimum-path-sum.py').Solution


def brute_force(grid: list[list[int]]) -> int:
    """Independent full-grid DP."""
    m, n = len(grid), len(grid[0])
    cost = [[0] * n for _ in range(m)]
    cost[0][0] = grid[0][0]
    for j in range(1, n):
        cost[0][j] = cost[0][j - 1] + grid[0][j]
    for i in range(1, m):
        cost[i][0] = cost[i - 1][0] + grid[i][0]
        for j in range(1, n):
            cost[i][j] = min(cost[i - 1][j], cost[i][j - 1]) + grid[i][j]
    return cost[m - 1][n - 1]


class MinimumPathSumTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().minPathSum

    def test_official_examples(self):
        self.assertEqual(self.solve([[1, 3, 1], [1, 5, 1], [4, 2, 1]]), 7)
        self.assertEqual(self.solve([[1, 2, 3], [4, 5, 6]]), 12)

    def test_single_cell(self):
        self.assertEqual(self.solve([[5]]), 5)
        self.assertEqual(self.solve([[0]]), 0)

    def test_single_row_and_column(self):
        self.assertEqual(self.solve([[1, 2, 3, 4]]), 10)
        self.assertEqual(self.solve([[1], [2], [3], [4]]), 10)

    def test_all_zeros(self):
        self.assertEqual(self.solve([[0] * 5 for _ in range(5)]), 0)

    def test_maximum_size(self):
        grid = [[200] * 200 for _ in range(200)]
        # Any monotone path takes exactly 399 steps of 200.
        self.assertEqual(self.solve(grid), 200 * 399)

    def test_exhaustive_small_grids(self):
        for m in range(1, 4):
            for n in range(1, 4):
                for cells in itertools.product(range(3), repeat=m * n):
                    grid = [list(cells[i * n:(i + 1) * n]) for i in range(m)]
                    with self.subTest(grid=grid):
                        self.assertEqual(self.solve([row[:] for row in grid]), brute_force(grid))

    def test_randomised_grids(self):
        rng = random.Random(64)
        for _ in range(60):
            m, n = rng.randint(1, 15), rng.randint(1, 15)
            grid = [[rng.randint(0, 200) for _ in range(n)] for _ in range(m)]
            with self.subTest(shape=(m, n)):
                self.assertEqual(self.solve([row[:] for row in grid]), brute_force(grid))


if __name__ == '__main__':
    unittest.main()
