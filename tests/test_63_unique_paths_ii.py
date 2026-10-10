import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('63-unique-paths-ii.py').Solution


def brute_force(grid: list[list[int]]) -> int:
    """Independent full-grid DP over the same recurrence."""
    m, n = len(grid), len(grid[0])
    ways = [[0] * n for _ in range(m)]
    if grid[0][0] == 0:
        ways[0][0] = 1
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 1:
                ways[i][j] = 0
                continue
            if i > 0:
                ways[i][j] += ways[i - 1][j]
            if j > 0:
                ways[i][j] += ways[i][j - 1]
    return ways[m - 1][n - 1]


class UniquePathsIITests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().uniquePathsWithObstacles

    def test_official_examples(self):
        self.assertEqual(self.solve([[0, 0, 0], [0, 1, 0], [0, 0, 0]]), 2)
        self.assertEqual(self.solve([[0, 1], [0, 0]]), 1)

    def test_single_cell(self):
        self.assertEqual(self.solve([[0]]), 1)
        self.assertEqual(self.solve([[1]]), 0)

    def test_blocked_start_or_end(self):
        self.assertEqual(self.solve([[1, 0], [0, 0]]), 0)
        self.assertEqual(self.solve([[0, 0], [0, 1]]), 0)

    def test_no_obstacles_matches_unique_paths(self):
        for m in range(1, 8):
            for n in range(1, 8):
                grid = [[0] * n for _ in range(m)]
                with self.subTest(m=m, n=n):
                    self.assertEqual(self.solve(grid), brute_force(grid))

    def test_wall_of_obstacles_blocks_everything(self):
        grid = [[0, 0, 0], [1, 1, 1], [0, 0, 0]]
        self.assertEqual(self.solve(grid), 0)

    def test_maximum_size(self):
        grid = [[0] * 100 for _ in range(100)]
        self.assertEqual(self.solve(grid), brute_force(grid))
        grid[50][50] = 1
        self.assertEqual(self.solve(grid), brute_force(grid))

    def test_exhaustive_small_grids(self):
        for m in range(1, 4):
            for n in range(1, 4):
                for cells in itertools.product([0, 1], repeat=m * n):
                    grid = [list(cells[i * n:(i + 1) * n]) for i in range(m)]
                    with self.subTest(grid=grid):
                        self.assertEqual(self.solve([row[:] for row in grid]), brute_force(grid))

    def test_randomised_grids(self):
        rng = random.Random(63)
        for _ in range(100):
            m, n = rng.randint(1, 12), rng.randint(1, 12)
            grid = [[1 if rng.random() < 0.25 else 0 for _ in range(n)] for _ in range(m)]
            with self.subTest(grid=grid):
                self.assertEqual(self.solve([row[:] for row in grid]), brute_force(grid))


if __name__ == '__main__':
    unittest.main()
