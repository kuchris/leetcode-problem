"""Tests for 90. Subsets II.

Oracle: every r-combination of the input for r = 0..len(nums), collected with
itertools into a set of frozensets. Duplicate inputs simply collapse in the set,
which is exactly the required "no duplicate subsets" rule, and it shares no code
with the sorted-backtracking solution under test.
"""

import itertools
import math
import random
import unittest
from collections import Counter

from _loader import load_solution

Solution = load_solution('90-subsets-ii.py').Solution


def brute_force(nums: list[int]) -> set[tuple[int, ...]]:
    """Every distinct subset as a sorted tuple.

    Tuples rather than frozensets: the input may repeat a value, and
    frozenset([2]) == frozenset([2, 2]) would silently merge [2] with [2, 2].
    """
    return {
        tuple(sorted(row))
        for size in range(len(nums) + 1)
        for row in itertools.combinations(nums, size)
    }


def expected_count(nums: list[int]) -> int:
    """Each distinct value contributes (copies + 1) independent choices."""
    return math.prod(count + 1 for count in Counter(nums).values())


def as_set(rows: list[list[int]]) -> set[tuple[int, ...]]:
    return {tuple(sorted(row)) for row in rows}


class SubsetsIITests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().subsetsWithDup

    def test_official_examples(self):
        result = self.solve([1, 2, 2])
        self.assertEqual(
            as_set(result),
            {(), (1,), (1, 2), (1, 2, 2), (2,), (2, 2)},
        )
        self.assertEqual(len(result), 6)
        self.assertEqual(as_set(self.solve([0])), {(), (0,)})

    def test_single_element(self):
        self.assertEqual(as_set(self.solve([7])), {(), (7,)})

    def test_all_values_identical(self):
        result = self.solve([2, 2, 2])
        self.assertEqual(
            as_set(result),
            {(), (2,), (2, 2), (2, 2, 2)},
        )
        self.assertEqual(len(result), 4)

    def test_all_values_distinct(self):
        nums = [1, 2, 3, 4]
        result = self.solve(nums)
        self.assertEqual(len(result), 2 ** len(nums))
        self.assertEqual(as_set(result), brute_force(nums))

    def test_negative_and_boundary_values(self):
        for nums in ([-10, -10, 10], [-10, 0, 10, 10], [10, 10, 10, -10]):
            with self.subTest(nums=nums):
                self.assertEqual(as_set(self.solve(nums)), brute_force(nums))

    def test_no_duplicate_subsets_and_every_subset_fits_the_input(self):
        nums = [4, 4, 4, 1, 1, 2]
        pool = Counter(nums)
        rows = self.solve(nums)
        self.assertEqual(len(rows), len(as_set(rows)))
        for row in rows:
            with self.subTest(row=row):
                used = Counter(row)
                self.assertTrue(all(used[value] <= pool[value] for value in used))
                self.assertEqual(sorted(row), row)

    def test_exhaustive_small_cases(self):
        for size in range(1, 7):
            for nums in itertools.combinations_with_replacement(range(-1, 2), size):
                nums = list(nums)
                with self.subTest(nums=nums):
                    result = self.solve(nums)
                    self.assertEqual(as_set(result), brute_force(nums))
                    self.assertEqual(len(result), len(as_set(result)))

    def test_randomised_cases(self):
        rng = random.Random(900)
        for _ in range(100):
            nums = [rng.randint(-2, 2) for _ in range(rng.randint(1, 10))]
            with self.subTest(nums=nums):
                result = self.solve(nums)
                self.assertEqual(as_set(result), brute_force(nums))
                self.assertEqual(len(result), expected_count(nums))

    def test_constraint_sized(self):
        # Ten elements is the constraint maximum, and ten copies of one value
        # gives the smallest answer the constraints allow.
        nums = [1] * 10
        result = self.solve(nums)
        self.assertEqual(len(result), 11)
        self.assertEqual(as_set(result), brute_force(nums))

        # Ten distinct values give the largest answer, 2^10 = 1024 subsets.
        nums = [-10, -9, -8, -7, -6, -5, -4, -3, -2, -1]
        result = self.solve(nums)
        self.assertEqual(len(result), 1024)
        self.assertEqual(as_set(result), brute_force(nums))

        # Mixed multiplicities: 5 * 4 * 4 = 80 subsets.
        nums = [1, 1, 1, 1, 2, 2, 2, 3, 3, 3]
        result = self.solve(nums)
        self.assertEqual(len(result), expected_count(nums))
        self.assertEqual(as_set(result), brute_force(nums))
        self.assertEqual(len(result), len(as_set(result)))


if __name__ == '__main__':
    unittest.main()
