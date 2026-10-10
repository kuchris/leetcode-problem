"""Tests for 81. Search in Rotated Sorted Array II.

Oracle: a plain linear membership test, which shares nothing with the binary
search under test and is obviously right for these small and mid-sized arrays.
"""

import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('81-search-in-rotated-sorted-array-ii.py').Solution


def brute_force(nums: list[int], target: int) -> bool:
    return target in nums


def rotations(values: list[int]):
    """Every rotation of a sorted array, i.e. every allowed pivot k."""
    for k in range(len(values)):
        yield values[k:] + values[:k]


class SearchInRotatedSortedArrayIITests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().search

    def test_official_examples(self):
        self.assertTrue(self.solve([2, 5, 6, 0, 0, 1, 2], 0))
        self.assertFalse(self.solve([2, 5, 6, 0, 0, 1, 2], 3))

    def test_single_element(self):
        self.assertTrue(self.solve([1], 1))
        self.assertFalse(self.solve([1], 0))
        self.assertFalse(self.solve([1], 2))
        self.assertFalse(self.solve([-10 ** 4], -10 ** 4 + 1))

    def test_no_rotation(self):
        nums = [0, 1, 2, 4, 5, 6, 7]
        for target in (-1, 0, 3, 4, 7, 8):
            with self.subTest(target=target):
                self.assertEqual(self.solve(nums, target), brute_force(nums, target))

    def test_all_values_equal(self):
        nums = [3] * 20
        self.assertTrue(self.solve(nums, 3))
        self.assertFalse(self.solve(nums, 2))
        self.assertFalse(self.solve(nums, 4))

    def test_duplicates_around_the_pivot(self):
        nums = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1]
        self.assertTrue(self.solve(nums, 2))
        self.assertFalse(self.solve(nums, 3))
        self.assertTrue(self.solve(nums, 1))

    def test_target_at_the_boundaries(self):
        nums = [4, 5, 6, 7, 0, 1, 2]
        self.assertTrue(self.solve(nums, 4))
        self.assertTrue(self.solve(nums, 2))
        self.assertFalse(self.solve(nums, 3))
        self.assertFalse(self.solve(nums, -1))
        self.assertFalse(self.solve(nums, 8))

    def test_boundary_values(self):
        nums = [-10 ** 4, -10 ** 4, 10 ** 4]
        self.assertTrue(self.solve(nums, -10 ** 4))
        self.assertTrue(self.solve(nums, 10 ** 4))
        self.assertFalse(self.solve(nums, 0))

    def test_exhaustive_small_cases(self):
        for size in range(1, 5):
            for values in itertools.combinations_with_replacement(range(3), size):
                for nums in rotations(list(values)):
                    for target in range(-1, 4):
                        with self.subTest(nums=nums, target=target):
                            self.assertEqual(self.solve(nums, target), brute_force(nums, target))

    def test_randomised_cases(self):
        rng = random.Random(810)
        for _ in range(200):
            size = rng.randint(1, 12)
            values = sorted(rng.randint(-3, 3) for _ in range(size))
            k = rng.randrange(size)
            nums = values[k:] + values[:k]
            for target in range(-4, 5):
                with self.subTest(nums=nums, target=target):
                    self.assertEqual(self.solve(nums, target), brute_force(nums, target))

    def test_constraint_sized(self):
        rng = random.Random(811)
        values = sorted(rng.randint(-10 ** 4, 10 ** 4) for _ in range(5000))
        k = rng.randrange(5000)
        nums = values[k:] + values[:k]
        self.assertEqual(len(nums), 5000)
        for target in [rng.randint(-10 ** 4, 10 ** 4) for _ in range(200)] + [values[0], values[-1]]:
            with self.subTest(target=target):
                self.assertEqual(self.solve(nums, target), brute_force(nums, target))

    def test_constraint_sized_worst_case_for_the_shrink_branch(self):
        # Every element equal defeats the "sorted half" test at every step, so
        # the search degrades to the O(n) duplicate-shrinking path.
        nums = [7] * 5000
        self.assertTrue(self.solve(nums, 7))
        self.assertFalse(self.solve(nums, 8))

        # Two equal outer values with a rotated middle: the same branch fires.
        nums = [1] * 2500 + [2, 3, 4] + [1] * 2497
        self.assertEqual(len(nums), 5000)
        for target in (1, 2, 3, 4, 0, 5):
            with self.subTest(target=target):
                self.assertEqual(self.solve(nums, target), brute_force(nums, target))


if __name__ == '__main__':
    unittest.main()
