"""Tests for 174. Dungeon Game.

Every oracle here walks *forward*, deliberately opposite to the backward DP
under test:

  - ``exhaustive_min_health``: enumerates every right/down path and takes the
    problem statement literally — a path needs ``1 - min(prefix sums)`` health
    (at least 1), and the answer is the cheapest path. No DP at all.
  - ``surviving_path``: a forward search over (row, column, health) that only
    walks while health stays positive. It never computes a requirement; it just
    tries to stay alive, which is exactly the question the solution inverts.
    The tests assert ``surviving_path(answer)`` exists and
    ``surviving_path(answer - 1)`` does not, so the returned health is proven
    both sufficient and minimal, and the surviving walk is replayed by
    ``simulate`` as a second, independent confirmation.
  - ``threshold_answer``: for the 200 x 200 cases, binary search the largest
    threshold every prefix sum of some path can meet (a forward DP under that
    threshold); the answer is then ``max(1, 1 - threshold)``. The threshold DP
    keeps the *maximum running sum* per cell, so it shares nothing with the
    backward requirement array.

Exhaustive sweep: every grid up to 2 x 3 over four values and every 3 x 3 grid
over two values, each checked against all three oracles.
"""

import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('174-dungeon-game.py').Solution

MIN_VALUE, MAX_VALUE = -1000, 1000
MAX_SIDE = 200


def all_paths(rows, cols):
    """Every right/down walk as a tuple of (row, column) cells."""
    moves = ['D'] * (rows - 1) + ['R'] * (cols - 1)
    for order in set(itertools.permutations(moves)):
        row = col = 0
        cells = [(0, 0)]
        for move in order:
            if move == 'D':
                row += 1
            else:
                col += 1
            cells.append((row, col))
        yield tuple(cells)


def exhaustive_min_health(grid) -> int:
    """The statement, transcribed: cheapest required health over all paths."""
    rows, cols = len(grid), len(grid[0])
    best = None
    for cells in all_paths(rows, cols):
        running = 0
        lowest = 0
        for row, col in cells:
            running += grid[row][col]
            lowest = min(lowest, running)
        needed = max(1, 1 - lowest)
        if best is None or needed < best:
            best = needed
    return best


def surviving_path(grid, initial_health):
    """A right/down walk that survives this initial health, or None.

    Forward only: states are (row, column, health), branches are abandoned as
    soon as health would reach 0, and repeats are pruned.
    """
    rows, cols = len(grid), len(grid[0])
    if initial_health <= 0:
        return None
    first = initial_health + grid[0][0]
    if first <= 0:
        return None
    stack = [(0, 0, first, ((0, 0),))]
    seen = set()
    while stack:
        row, col, health, path = stack.pop()
        if row == rows - 1 and col == cols - 1:
            return list(path)
        if (row, col, health) in seen:
            continue
        seen.add((row, col, health))
        for next_row, next_col in ((row + 1, col), (row, col + 1)):
            if next_row < rows and next_col < cols:
                next_health = health + grid[next_row][next_col]
                if next_health > 0:
                    stack.append(
                        (next_row, next_col, next_health, path + ((next_row, next_col),))
                    )
    return None


def simulate(grid, path, initial_health) -> bool:
    """Replay a walk and report whether health stays positive throughout."""
    health = initial_health
    for row, col in path:
        health += grid[row][col]
        if health <= 0:
            return False
    return True


def threshold_answer(grid) -> int:
    """max(1, 1 - X) for the largest X every prefix sum of some path can meet."""
    rows, cols = len(grid), len(grid[0])
    lowest_cell = min(min(row) for row in grid)
    largest_cell = max(max(row) for row in grid)
    lo = lowest_cell * (rows + cols - 1)
    hi = max(largest_cell * (rows + cols - 1),
             sum(max(0, value) for row in grid for value in row))

    def feasible(threshold) -> bool:
        """Can some path keep every prefix sum >= threshold?

        Per cell only the largest reachable running sum matters: any
        continuation available from a smaller sum is available from a larger one.
        """
        running = [[None] * cols for _ in range(rows)]
        for i in range(rows):
            for j in range(cols):
                if i == 0 and j == 0:
                    total = grid[0][0]
                else:
                    candidates = []
                    if i > 0 and running[i - 1][j] is not None:
                        candidates.append(running[i - 1][j])
                    if j > 0 and running[i][j - 1] is not None:
                        candidates.append(running[i][j - 1])
                    if not candidates:
                        continue
                    total = max(candidates) + grid[i][j]
                running[i][j] = total if total >= threshold else None
        return running[rows - 1][cols - 1] is not None

    while lo < hi:
        middle = (lo + hi + 1) // 2
        if feasible(middle):
            lo = middle
        else:
            hi = middle - 1
    return max(1, 1 - lo)


class DungeonGameTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().calculateMinimumHP

    def check(self, grid):
        answer = self.solve([list(row) for row in grid])
        self.assertEqual(answer, exhaustive_min_health(grid))
        self.assertEqual(answer, threshold_answer(grid))
        return answer

    def test_official_examples(self):
        self.assertEqual(
            self.solve([[-2, -3, 3], [-5, -10, 1], [10, 30, -5]]), 7
        )
        self.assertEqual(self.solve([[0]]), 1)
        self.check([[-2, -3, 3], [-5, -10, 1], [10, 30, -5]])
        self.check([[0]])

    def test_single_cell(self):
        self.assertEqual(self.solve([[-1000]]), 1001)
        self.assertEqual(self.solve([[-1]]), 2)
        self.assertEqual(self.solve([[0]]), 1)
        self.assertEqual(self.solve([[1]]), 1)
        self.assertEqual(self.solve([[1000]]), 1)

    def test_single_row_and_single_column(self):
        self.assertEqual(self.solve([[-5, 1000]]), 6)
        self.assertEqual(self.solve([[1000, -5]]), 1)
        self.assertEqual(self.solve([[-3, -4, -5]]), 13)
        self.assertEqual(self.solve([[-3], [4]]), 4)
        self.assertEqual(self.solve([[4], [-3]]), 1)
        self.check([[-5, 1000]])
        self.check([[-3, -4, -5]])
        self.check([[4], [-3]])

    def test_solution_is_sufficient_and_minimal(self):
        grid = [[-2, -3, 3], [-5, -10, 1], [10, 30, -5]]
        answer = self.solve(grid)
        path = surviving_path(grid, answer)
        self.assertIsNotNone(path)
        self.assertEqual(path[0], (0, 0))
        self.assertEqual(path[-1], (len(grid) - 1, len(grid[0]) - 1))
        for (row, col), (next_row, next_col) in zip(path, path[1:]):
            self.assertIn((next_row - row, next_col - col), ((1, 0), (0, 1)))
        self.assertTrue(simulate(grid, path, answer))
        self.assertIsNone(surviving_path(grid, answer - 1))

    def test_exhaustive_small_grids(self):
        for rows, cols, alphabet in (
            (1, 1, (-2, -1, 0, 3)),
            (1, 2, (-2, -1, 0, 3)),
            (2, 1, (-2, -1, 0, 3)),
            (2, 2, (-2, -1, 0, 3)),
            (2, 3, (-1, 2)),
            (3, 2, (-1, 2)),
            (3, 3, (-1, 2)),
        ):
            for flat in itertools.product(alphabet, repeat=rows * cols):
                grid = [
                    list(flat[index * cols:(index + 1) * cols])
                    for index in range(rows)
                ]
                with self.subTest(grid=grid):
                    self.check(grid)

    def test_random_grids_with_sufficiency(self):
        rng = random.Random(1740)
        for case in range(400):
            rows = rng.randint(1, 5)
            cols = rng.randint(1, 5)
            grid = [
                [rng.randint(-6, 6) for _ in range(cols)] for _ in range(rows)
            ]
            with self.subTest(case=case, grid=grid):
                answer = self.check(grid)
                path = surviving_path(grid, answer)
                self.assertIsNotNone(path)
                self.assertTrue(simulate(grid, path, answer))
                if answer > 1:
                    self.assertIsNone(surviving_path(grid, answer - 1))

    def test_constraint_sized_shapes(self):
        # Uniform extremes at 200 x 200: every path has the same 399 rooms.
        all_negative = [[-1000] * MAX_SIDE for _ in range(MAX_SIDE)]
        self.assertEqual(self.solve(all_negative), 399 * 1000 + 1)
        all_positive = [[1000] * MAX_SIDE for _ in range(MAX_SIDE)]
        self.assertEqual(self.solve(all_positive), 1)

        # A wide and a tall strip.
        strip = [[-3] * MAX_SIDE]
        self.assertEqual(self.solve(strip), 3 * MAX_SIDE + 1)
        column = [[-3] for _ in range(MAX_SIDE)]
        self.assertEqual(self.solve(column), 3 * MAX_SIDE + 1)

        # Every room terrible except the princess room.
        rng = random.Random(1741)
        grid = [[rng.randint(-1000, -900) for _ in range(MAX_SIDE)]
                for _ in range(MAX_SIDE)]
        self.assertEqual(self.solve(grid), threshold_answer(grid))

    def test_constraint_sized_random(self):
        rng = random.Random(1742)
        for case in range(3):
            grid = [[rng.randint(MIN_VALUE, MAX_VALUE) for _ in range(MAX_SIDE)]
                    for _ in range(MAX_SIDE)]
            with self.subTest(case=case):
                self.assertEqual(self.solve(grid), threshold_answer(grid))

        # A single huge orb at the far corner, everything else negative.
        grid = [[-1000] * MAX_SIDE for _ in range(MAX_SIDE)]
        grid[MAX_SIDE - 1][MAX_SIDE - 1] = 1000
        self.assertEqual(self.solve(grid), threshold_answer(grid))


if __name__ == '__main__':
    unittest.main()
