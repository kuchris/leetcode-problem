"""Tests for 78. Subsets.

Oracle: every r-combination of the input for r = 0..len(nums), collected by
itertools, compared as a set of frozensets so the unspecified output order is
irrelevant.
"""

import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('78-subsets.py').Solution


def brute_force(nums: list[int]) -> set[frozenset]:
    """The power set built from itertools.combinations."""
    return {
        frozenset(row)
        for size in range(len(nums) + 1)
        for row in itertools.combinations(nums, size)
    }


def as_set(rows: list[list[int]]) -> set[frozenset]:
    return {frozenset(row) for row in rows}


class SubsetsTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().subsets

    def test_official_examples(self):
        result = self.solve([1, 2, 3])
        self.assertEqual(len(result), 8)
        self.assertEqual(
            as_set(result),
            {frozenset(), frozenset([1]), frozenset([2]), frozenset([1, 2]),
             frozenset([3]), frozenset([1, 3]), frozenset([2, 3]),
             frozenset([1, 2, 3])},
        )
        self.assertEqual(as_set(self.solve([0])), {frozenset(), frozenset([0])})

    def test_single_element(self):
        result = self.solve([5])
        self.assertEqual(len(result), 2)
        self.assertEqual(as_set(result), {frozenset(), frozenset([5])})

    def test_two_elements(self):
        self.assertEqual(
            as_set(self.solve([1, 2])),
            {frozenset(), frozenset([1]), frozenset([2]), frozenset([1, 2])},
        )

    def test_negative_and_boundary_values(self):
        nums = [-10, 10, 0]
        self.assertEqual(as_set(self.solve(nums)), brute_force(nums))
        self.assertEqual(as_set(self.solve([-10, 10])), brute_force([-10, 10]))

    def test_output_has_no_duplicates_and_only_input_values(self):
        nums = [3, -1, 7, -8, 0]
        rows = self.solve(nums)
        self.assertEqual(len(rows), 2 ** len(nums))
        self.assertEqual(len(as_set(rows)), 2 ** len(nums))
        for row in rows:
            self.assertEqual(len(set(row)), len(row))
            self.assertTrue(set(row) <= set(nums))

    def test_exhaustive_small_cases(self):
        for size in range(1, 6):
            for nums in itertools.permutations(range(size)):
                nums = list(nums)
                with self.subTest(nums=nums):
                    self.assertEqual(as_set(self.solve(nums)), brute_force(nums))

    def test_randomised_cases(self):
        rng = random.Random(780)
        for _ in range(50):
            nums = rng.sample(range(-10, 11), rng.randint(1, 9))
            with self.subTest(nums=nums):
                self.assertEqual(as_set(self.solve(nums)), brute_force(nums))

    def test_constraint_sized(self):
        # Ten unique values is the constraint maximum: 2^10 = 1024 subsets.
        nums = [-10, 10, 0, 5, -7, 3, 9, -1, 8, -3]
        rows = self.solve(nums)
        self.assertEqual(len(rows), 1024)
        self.assertEqual(as_set(rows), brute_force(nums))
        self.assertIn([], rows)
        self.assertIn(nums, rows)


if __name__ == '__main__':
    unittest.main()
