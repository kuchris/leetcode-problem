"""Tests for 135. Candy.

The oracle is a from-scratch two-pass count written in a different shape from
the solution: instead of carrying a running maximum, it measures the length of
the strictly increasing run that ends at (and starts at) each position, takes the
pointwise maximum of the two run lengths, and sums that. Because the two-pass
bound is easy to get subtly wrong, the oracle is itself validated against an
honest brute force -- the minimum total over every assignment in [1..n]^n that
satisfies both neighbour rules -- on small ratings, and the assignment it implies
is checked to be feasible.
"""

import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('135-candy.py').Solution


def run_lengths(ratings):
    """(left, right) run-length bounds: 1 + the length of the increasing run."""
    n = len(ratings)
    left = [1] * n
    length = 1
    for index in range(1, n):
        length = length + 1 if ratings[index] > ratings[index - 1] else 1
        left[index] = length
    right = [1] * n
    length = 1
    for index in range(n - 2, -1, -1):
        length = length + 1 if ratings[index] > ratings[index + 1] else 1
        right[index] = length
    return left, right


def oracle_assignment(ratings) -> list:
    """The minimal assignment implied by the two directional run bounds."""
    left, right = run_lengths(ratings)
    return [max(a, b) for a, b in zip(left, right)]


def oracle(ratings) -> int:
    return sum(oracle_assignment(ratings))


def is_feasible(ratings, candies) -> bool:
    """Every child gets at least one candy; higher ratings get more."""
    if any(count < 1 for count in candies):
        return False
    for index in range(len(ratings) - 1):
        if ratings[index] > ratings[index + 1] and candies[index] <= candies[index + 1]:
            return False
        if ratings[index] < ratings[index + 1] and candies[index] >= candies[index + 1]:
            return False
    return True


def brute_force(ratings) -> int:
    """Minimum total over every assignment in [1..n]^n that is feasible."""
    n = len(ratings)
    best = None
    for assignment in itertools.product(range(1, n + 1), repeat=n):
        if not is_feasible(ratings, assignment):
            continue
        total = sum(assignment)
        if best is None or total < best:
            best = total
    return best


class CandyTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().candy

    def test_official_examples(self):
        self.assertEqual(self.solve([1, 0, 2]), 5)
        self.assertEqual(self.solve([1, 2, 2]), 4)

    def test_single_child(self):
        for rating in (0, 1, 5 * 10 ** 4):
            with self.subTest(rating=rating):
                self.assertEqual(self.solve([rating]), 1)

    def test_two_children(self):
        self.assertEqual(self.solve([1, 1]), 2)
        self.assertEqual(self.solve([1, 2]), 3)
        self.assertEqual(self.solve([2, 1]), 3)
        self.assertEqual(self.solve([0, 5 * 10 ** 4]), 3)

    def test_all_equal(self):
        for size in (1, 2, 10, 1000):
            with self.subTest(size=size):
                self.assertEqual(self.solve([7] * size), size)

    def test_monotone_runs(self):
        self.assertEqual(self.solve([1, 2, 3, 4]), 10)
        self.assertEqual(self.solve([4, 3, 2, 1]), 10)
        self.assertEqual(self.solve([1, 2, 3, 2, 1]), 9)

    def test_plateaus(self):
        self.assertEqual(self.solve([1, 1, 2]), 4)
        self.assertEqual(self.solve([2, 1, 1]), 4)
        self.assertEqual(self.solve([1, 2, 2, 1]), 6)
        # A plateau between two valleys only needs its ramp edges raised, so the
        # total is 1 + 2 + 1 + 2 + 1 (confirmed against brute force below).
        self.assertEqual(self.solve([1, 2, 2, 2, 1]), 7)

    def test_oracle_is_validated_by_brute_force(self):
        # The oracle must equal an exhaustive search, and the assignment it
        # describes must actually satisfy the rules.
        for size in range(1, 5):
            for ratings in itertools.product(range(3), repeat=size):
                ratings = list(ratings)
                with self.subTest(ratings=ratings):
                    self.assertEqual(oracle(ratings), brute_force(ratings))
                    self.assertTrue(is_feasible(ratings, oracle_assignment(ratings)))

        rng = random.Random(1350)
        for _ in range(30):
            ratings = [rng.randint(0, 4) for _ in range(5)]
            with self.subTest(ratings=ratings):
                self.assertEqual(oracle(ratings), brute_force(ratings))
                self.assertTrue(is_feasible(ratings, oracle_assignment(ratings)))

        # Hand-picked plateaus, including the one this file asserts by hand.
        for ratings in ([1, 2, 2, 2, 1], [1, 2, 2, 1], [2, 1, 1, 2], [1, 1, 1, 2, 3]):
            with self.subTest(ratings=ratings):
                self.assertEqual(oracle(ratings), brute_force(ratings))
                self.assertTrue(is_feasible(ratings, oracle_assignment(ratings)))

    def test_exhaustive_small_cases(self):
        for size in range(1, 7):
            for ratings in itertools.product(range(3), repeat=size):
                ratings = list(ratings)
                with self.subTest(ratings=ratings):
                    self.assertEqual(self.solve(ratings), oracle(ratings))

    def test_exhaustive_small_cases_four_values(self):
        for size in range(1, 6):
            for ratings in itertools.product(range(4), repeat=size):
                ratings = list(ratings)
                with self.subTest(ratings=ratings):
                    self.assertEqual(self.solve(ratings), oracle(ratings))

    def test_randomised_cases(self):
        rng = random.Random(1351)
        for _ in range(400):
            size = rng.randint(1, 120)
            ratings = [rng.randint(0, 6) for _ in range(size)]
            with self.subTest(size=size):
                self.assertEqual(self.solve(ratings), oracle(ratings))

    def test_randomised_extreme_ratings(self):
        rng = random.Random(1352)
        for _ in range(200):
            size = rng.randint(1, 60)
            ratings = [rng.choice([0, 5 * 10 ** 4]) for _ in range(size)]
            with self.subTest(size=size):
                self.assertEqual(self.solve(ratings), oracle(ratings))

    def test_constraint_sized(self):
        # 5 * 10^4 children is the constraint maximum.
        size = 5 * 10 ** 4

        increasing = list(range(size))
        self.assertEqual(self.solve(increasing), size * (size + 1) // 2)
        self.assertEqual(self.solve(increasing[::-1]), size * (size + 1) // 2)

        self.assertEqual(self.solve([5 * 10 ** 4] * size), size)
        self.assertEqual(self.solve([0] * size), size)

        # A long plateau then a spike: only the spike neighbours differ.
        plateau = [5] * size
        plateau[-1] = 6
        self.assertEqual(self.solve(plateau), size + 1)

        zigzag = [index % 2 for index in range(size)]
        self.assertEqual(self.solve(zigzag), oracle(zigzag))

        rng = random.Random(1353)
        ratings = [rng.randint(0, 5 * 10 ** 4) for _ in range(size)]
        self.assertEqual(self.solve(ratings), oracle(ratings))

        # Sawtooth and triangle waves: every run is bounded and the ratings stay
        # inside [0, 5 * 10^4].
        sawtooth = [index % 100 for index in range(size)]
        self.assertEqual(self.solve(sawtooth), oracle(sawtooth))

        triangle = [min(index % 200, 200 - index % 200) for index in range(size)]
        self.assertEqual(self.solve(triangle), oracle(triangle))

        # A long staircase: strictly increasing except for a reset every 1000.
        staircase = [(index // 1000) * 1000 + index % 1000 for index in range(size)]
        self.assertTrue(all(0 <= value <= 5 * 10 ** 4 for value in staircase))
        self.assertEqual(self.solve(staircase), oracle(staircase))


if __name__ == '__main__':
    unittest.main()
