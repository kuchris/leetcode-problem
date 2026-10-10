"""Tests for 149. Max Points on a Line.

Oracles:
  - ``brute_force_cross``: every pair defines a line, then every point is tested
    against it with the integer determinant ``dx * (y3 - y1) - dy * (x3 - x1)``.
    No slopes, no division, no floats — it shares nothing with the solution's
    reduced-direction dictionary.
  - ``fraction_oracle``: per anchor, ``fractions.Fraction`` slopes reduced by the
    standard library, plus an explicit duplicate count. Used for the 300-point
    cases where the O(n^3) oracle would be too slow; exact for the same reason.

The float trap is tested directly: pairs of points whose true slopes differ by
the smallest difference the coordinate range allows must never be merged.

The statement guarantees "all the points are unique", so duplicate coordinates
sit in one clearly labelled robustness test instead of the guarantee-respecting
sweeps; the solution and both oracles handle them anyway.
"""

import collections
import itertools
import random
import unittest
from fractions import Fraction

from _loader import load_solution

Solution = load_solution('149-max-points-on-a-line.py').Solution

MAX_POINTS = 300
MAX_COORD = 10 ** 4
GRID = [(x, y) for x in range(3) for y in range(3)]


def brute_force_cross(points) -> int:
    """Count, for every pair, all points on that line — exact integers."""
    size = len(points)
    if size <= 2:
        return size
    best = 1
    # Coincident points lie on every line through that point, so they have to
    # be counted separately: a coincident pair defines no direction at all, and
    # testing other points against its zero vector would accept all of them.
    for i in range(size):
        best = max(best, sum(1 for point in points if point == points[i]))
    for i in range(size):
        x1, y1 = points[i]
        for j in range(i + 1, size):
            x2, y2 = points[j]
            dx = x2 - x1
            dy = y2 - y1
            if dx == 0 and dy == 0:
                continue
            count = 0
            for k in range(size):
                x3, y3 = points[k]
                if dx * (y3 - y1) - dy * (x3 - x1) == 0:
                    count += 1
            best = max(best, count)
    return best


def fraction_oracle(points) -> int:
    """Per-anchor exact rational slopes plus a duplicate count."""
    best = 1
    for i, (x1, y1) in enumerate(points):
        slopes = collections.Counter()
        same = 0
        for j, (x2, y2) in enumerate(points):
            if i == j:
                continue
            dx = x2 - x1
            dy = y2 - y1
            if dx == 0 and dy == 0:
                same += 1
                continue
            # Fraction reduces exactly; None marks the vertical direction.
            slopes[None if dx == 0 else Fraction(dy, dx)] += 1
        best = max(best, same + 1 + max(slopes.values(), default=0))
    return best


class MaxPointsOnALineTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().maxPoints

    def check(self, points):
        result = self.solve(points)
        self.assertEqual(result, brute_force_cross(points))
        self.assertEqual(result, fraction_oracle(points))
        return result

    def test_official_examples(self):
        self.assertEqual(self.solve([[1, 1], [2, 2], [3, 3]]), 3)
        self.assertEqual(
            self.solve([[1, 1], [3, 2], [5, 3], [4, 1], [2, 3], [1, 4]]), 4
        )

    def test_one_and_two_points(self):
        self.assertEqual(self.solve([[0, 0]]), 1)
        self.assertEqual(self.solve([[MAX_COORD, -MAX_COORD]]), 1)
        self.assertEqual(self.solve([[0, 0], [1, 1]]), 2)
        self.assertEqual(self.solve([[0, 0], [0, 5]]), 2)

    def test_vertical_and_horizontal_lines(self):
        vertical = [[0, y] for y in range(5)]
        horizontal = [[x, 7] for x in range(5)]
        self.assertEqual(self.solve(vertical), 5)
        self.assertEqual(self.solve(horizontal), 5)
        # A cross: neither arm beats the longer one.
        self.assertEqual(self.solve([[0, 0], [0, 1], [0, 2], [1, 0], [2, 0]]), 3)
        self.check([[0, 0], [0, 1], [0, 2], [1, 0], [2, 0], [3, 3], [4, 4]])

    def test_opposite_directions_collapse(self):
        # The same line is walked with dx > 0 and dx < 0.
        self.assertEqual(self.solve([[0, 0], [1, 1], [-1, -1], [2, 2]]), 4)
        self.assertEqual(self.solve([[-2, -4], [-1, -2], [0, 0], [1, 2], [2, 4]]), 5)

    def test_slopes_that_are_close_are_not_merged(self):
        # 9999/10000 and 9998/9999 differ; the determinant is 1, not 0.
        self.assertEqual(self.solve([[0, 0], [10000, 9999], [9999, 9998]]), 2)
        # Exactly equal ratios must still merge: 1/3 == 2/6 == 3/9.
        self.assertEqual(self.solve([[0, 0], [3, 1], [6, 2], [9, 3]]), 4)
        # And a neighbour that is one unit off the line must not.
        self.assertEqual(self.solve([[0, 0], [3, 1], [6, 2], [9, 4]]), 3)
        self.check([[0, 0], [3, 1], [6, 2], [9, 4], [12, 4]])

    def test_exhaustive_small_point_sets(self):
        for size in range(1, 6):
            for points in itertools.combinations(GRID, size):
                points = [list(point) for point in points]
                with self.subTest(points=points):
                    self.check(points)

    def test_random_small_sets(self):
        rng = random.Random(1490)
        universe = [(x, y) for x in range(-4, 5) for y in range(-4, 5)]
        for _ in range(400):
            size = rng.randint(1, 20)
            points = [list(point) for point in rng.sample(universe, size)]
            with self.subTest(points=points[:6]):
                self.check(points)

    def test_random_sets_with_repeated_values_on_one_line(self):
        # Lines built from small primitive directions, which is where a
        # float-based slope map would start merging neighbouring directions.
        rng = random.Random(1491)
        for _ in range(200):
            dx, dy = rng.randint(1, 5), rng.randint(-5, 5)
            step = rng.randint(1, 4)
            anchor_x, anchor_y = rng.randint(-20, 20), rng.randint(-20, 20)
            line = [
                [anchor_x + step * k * dx, anchor_y + step * k * dy]
                for k in range(rng.randint(2, 8))
            ]
            noise = [
                [rng.randint(-30, 30), rng.randint(-30, 30)]
                for _ in range(rng.randint(0, 6))
            ]
            points = line + noise
            self.assertEqual(len({tuple(point) for point in points}), len(points))
            with self.subTest(dx=dx, dy=dy, size=len(points)):
                self.check(points)

    def test_duplicate_coordinates_outside_the_guarantee(self):
        # The statement says every point is unique; these cases only document
        # that duplicates do not break the counting.
        self.assertEqual(self.solve([[1, 1], [1, 1], [2, 2]]), 3)
        self.assertEqual(self.solve([[0, 0], [0, 0], [0, 0]]), 3)
        self.assertEqual(self.solve([[1, 2], [1, 2], [3, 4], [5, 6]]), 4)
        self.assertEqual(self.solve([[0, 0], [0, 0], [1, 1], [2, 3]]), 3)
        self.check([[1, 1], [1, 1], [2, 2], [4, 9]])
        self.check([[0, 0]] * 4 + [[1, 5], [2, 9]])

    def test_constraint_sized(self):
        # 300 points on one line: the coordinate bounds allow y = 2x + 3.
        collinear = [[x, 2 * x + 3] for x in range(MAX_POINTS)]
        self.assertEqual(len(collinear), MAX_POINTS)
        self.assertTrue(all(abs(y) <= MAX_COORD for _, y in collinear))
        self.assertEqual(self.solve(collinear), MAX_POINTS)

        # A full 17 x 17 grid: a line meets a k x k grid in at most k points
        # (distinct x per row, or one per row when vertical), and rows reach it.
        side = 17
        grid = [[x, y] for x in range(side) for y in range(side)]
        self.assertEqual(len(grid), side * side)
        self.assertEqual(self.solve(grid), side)
        self.assertEqual(fraction_oracle(grid), side)

        # Random unique points over the whole coordinate range.
        rng = random.Random(1492)
        seen = set()
        points = []
        while len(points) < MAX_POINTS:
            point = (rng.randint(-MAX_COORD, MAX_COORD), rng.randint(-MAX_COORD, MAX_COORD))
            if point in seen:
                continue
            seen.add(point)
            points.append([point[0], point[1]])
        self.assertEqual(self.solve(points), fraction_oracle(points))

        # One long line plus scattered noise: the answer is the long line.
        line = [[x, x] for x in range(150)]
        noise = []
        while len(noise) < MAX_POINTS - 150:
            point = (rng.randint(-MAX_COORD, MAX_COORD), rng.randint(-MAX_COORD, MAX_COORD))
            if point[1] != point[0]:
                noise.append([point[0], point[1]])
        points = line + noise
        self.assertEqual(self.solve(points), fraction_oracle(points))
        self.assertGreaterEqual(self.solve(points), 150)


if __name__ == '__main__':
    unittest.main()
