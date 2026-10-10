"""Tests for 120. Triangle.

Oracles:
  - ``brute_force``: enumerate every top-to-bottom path with a DFS and keep the
    cheapest, i.e. the statement itself, exponential but exact.
  - ``top_down``: a forward DP that stores the cheapest cost *to* each cell,
    the opposite direction from the solution's bottom-up rolling array. It is
    the oracle for the 200-row constraint case, where the DFS is hopeless.
  - closed forms for the uniform-value cases: every path visits exactly one cell
    per row, so an all-negative triangle costs 200 * value and an all-positive
    one the same, making 200 the only legal path length.

Exhaustive sweep: every triangle with up to three rows over three values and
every four-row triangle over two values, each checked against both oracles.
"""

import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('120-triangle.py').Solution

MAX_LAYERS = 200
LIMIT = 10 ** 4


def brute_force(triangle) -> int:
    """The literal definition: walk every path, keep the cheapest total."""
    best = [None]

    def walk(row, index, total):
        total += triangle[row][index]
        if row == len(triangle) - 1:
            if best[0] is None or total < best[0]:
                best[0] = total
            return
        walk(row + 1, index, total)
        walk(row + 1, index + 1, total)

    walk(0, 0, 0)
    return best[0]


def top_down(triangle) -> int:
    """Forward DP: costs[j] is the cheapest cost reaching row cell j.

    The answer is the cheapest cell of the *last* row, not necessarily its
    first cell, so the final step is a minimum over the whole row.
    """
    costs = [triangle[0][0]]
    for row in triangle[1:]:
        costs = (
            [row[0] + costs[0]]
            + [row[j] + min(costs[j - 1], costs[j]) for j in range(1, len(row) - 1)]
            + [row[-1] + costs[-1]]
        )
    return min(costs)


def triangle_from_flat(flat, layers) -> list:
    rows = []
    position = 0
    for length in range(1, layers + 1):
        rows.append(list(flat[position:position + length]))
        position += length
    return rows


class TriangleTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().minimumTotal

    def test_official_examples(self):
        self.assertEqual(self.solve([[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]]), 11)
        self.assertEqual(self.solve([[-10]]), -10)

    def test_smallest_triangles(self):
        self.assertEqual(self.solve([[0]]), 0)
        self.assertEqual(self.solve([[7]]), 7)
        self.assertEqual(self.solve([[1], [2, 3]]), 3)
        self.assertEqual(self.solve([[1], [3, 2]]), 3)
        self.assertEqual(self.solve([[-1], [-2, -3]]), -4)

    def test_all_negative_prefers_the_deepest_descent(self):
        # The paths cost -7, 2, 1 and -10, so the all-negative column wins.
        triangle = [[-1], [-2, -3], [-4, 5, -6]]
        self.assertEqual(self.solve(triangle), brute_force(triangle))
        self.assertEqual(self.solve(triangle), -10)

    def test_greedy_choice_is_not_enough(self):
        # Taking the smallest neighbour immediately loses later: 1 -> 2 -> 100
        # costs 103, while 1 -> 3 -> 0 costs 4.
        triangle = [[1], [2, 3], [100, 100, 0]]
        self.assertEqual(self.solve(triangle), 4)
        self.assertEqual(brute_force(triangle), 4)

    def test_exhaustive_small_triangles(self):
        for layers in (1, 2, 3):
            cells = layers * (layers + 1) // 2
            for flat in itertools.product((-2, 0, 3), repeat=cells):
                triangle = triangle_from_flat(flat, layers)
                with self.subTest(layers=layers, triangle=triangle):
                    self.assertEqual(self.solve(triangle), brute_force(triangle))
                    self.assertEqual(self.solve(triangle), top_down(triangle))
        for flat in itertools.product((0, 1), repeat=10):
            triangle = triangle_from_flat(flat, 4)
            with self.subTest(layers=4, triangle=triangle):
                self.assertEqual(self.solve(triangle), brute_force(triangle))
                self.assertEqual(self.solve(triangle), top_down(triangle))

    def test_random_triangles_against_both_oracles(self):
        rng = random.Random(1200)
        for _ in range(400):
            layers = rng.randint(1, 8)
            cells = layers * (layers + 1) // 2
            flat = [rng.randint(-50, 50) for _ in range(cells)]
            triangle = triangle_from_flat(flat, layers)
            with self.subTest(triangle=triangle):
                self.assertEqual(self.solve(triangle), brute_force(triangle))
                self.assertEqual(self.solve(triangle), top_down(triangle))

    def test_input_is_not_mutated(self):
        triangle = [[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]]
        copy = [list(row) for row in triangle]
        self.solve(triangle)
        self.assertEqual(triangle, copy)

    def test_constraint_sized(self):
        rng = random.Random(1201)
        triangle = [
            [rng.randint(-LIMIT, LIMIT) for _ in range(length)]
            for length in range(1, MAX_LAYERS + 1)
        ]
        self.assertEqual(self.solve(triangle), top_down(triangle))

        # Every path takes one cell per row, so uniform values pin the answer.
        self.assertEqual(
            self.solve([[-LIMIT] * length for length in range(1, MAX_LAYERS + 1)]),
            -LIMIT * MAX_LAYERS,
        )
        self.assertEqual(
            self.solve([[LIMIT] * length for length in range(1, MAX_LAYERS + 1)]),
            LIMIT * MAX_LAYERS,
        )

        # A single-row triangle at each extreme.
        self.assertEqual(self.solve([[-LIMIT]]), -LIMIT)
        self.assertEqual(self.solve([[LIMIT]]), LIMIT)


if __name__ == '__main__':
    unittest.main()
