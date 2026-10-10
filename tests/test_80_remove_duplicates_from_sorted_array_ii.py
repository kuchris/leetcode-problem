"""Tests for 80. Remove Duplicates from Sorted Array II.

Oracle: itertools.groupby over the sorted input, keeping min(run length, 2) of
each value -- a direct transcription of the requirement, with no write pointer.
"""

import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('80-remove-duplicates-from-sorted-array-ii.py').Solution


def brute_force(nums: list[int]) -> list[int]:
    """Expected prefix: every run truncated to at most two copies."""
    expected: list[int] = []
    for value, group in itertools.groupby(nums):
        expected.extend([value] * min(len(list(group)), 2))
    return expected


class RemoveDuplicatesFromSortedArrayIITests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().removeDuplicates

    def apply(self, nums):
        work = list(nums)
        k = self.solve(work)
        return k, work

    def test_official_examples(self):
        k, work = self.apply([1, 1, 1, 2, 2, 3])
        self.assertEqual(k, 5)
        self.assertEqual(work[:k], [1, 1, 2, 2, 3])

        k, work = self.apply([0, 0, 1, 1, 1, 1, 2, 3, 3])
        self.assertEqual(k, 7)
        self.assertEqual(work[:k], [0, 0, 1, 1, 2, 3, 3])

    def test_single_element(self):
        k, work = self.apply([1])
        self.assertEqual((k, work[:k]), (1, [1]))
        k, work = self.apply([-10 ** 4])
        self.assertEqual((k, work[:k]), (1, [-10 ** 4]))

    def test_two_elements(self):
        k, work = self.apply([2, 2])
        self.assertEqual((k, work[:k]), (2, [2, 2]))
        k, work = self.apply([1, 2])
        self.assertEqual((k, work[:k]), (2, [1, 2]))

    def test_all_values_equal(self):
        k, work = self.apply([7] * 10)
        self.assertEqual((k, work[:k]), (2, [7, 7]))

    def test_all_values_distinct(self):
        nums = [1, 2, 3, 4, 5]
        k, work = self.apply(nums)
        self.assertEqual((k, work[:k]), (5, nums))

    def test_three_copies_become_two(self):
        k, work = self.apply([1, 1, 1])
        self.assertEqual((k, work[:k]), (2, [1, 1]))

    def test_boundary_values(self):
        nums = [-10 ** 4, -10 ** 4, -10 ** 4, 0, 10 ** 4, 10 ** 4, 10 ** 4]
        k, work = self.apply(nums)
        self.assertEqual((k, work[:k]), (5, [-10 ** 4, -10 ** 4, 0, 10 ** 4, 10 ** 4]))

    def test_returns_int_and_keeps_the_prefix_sorted(self):
        work = [1, 1, 1, 2, 2, 3]
        k = self.solve(work)
        self.assertIsInstance(k, int)
        self.assertEqual(work[:k], sorted(work[:k]))
        self.assertEqual(len(work[:k]), k)

    def test_no_run_keeps_more_than_two_copies(self):
        nums = [1, 1, 1, 2, 2, 2, 3, 4, 4, 4, 4]
        k, work = self.apply(nums)
        for value, group in itertools.groupby(work[:k]):
            with self.subTest(value=value):
                self.assertLessEqual(len(list(group)), 2)

    def test_exhaustive_small_cases(self):
        for size in range(1, 8):
            for nums in itertools.combinations_with_replacement(range(3), size):
                nums = list(nums)
                with self.subTest(nums=nums):
                    k, work = self.apply(nums)
                    expected = brute_force(nums)
                    self.assertEqual(k, len(expected))
                    self.assertEqual(work[:k], expected)

    def test_randomised_cases(self):
        rng = random.Random(800)
        for _ in range(300):
            nums = sorted(rng.randint(-5, 5) for _ in range(rng.randint(1, 60)))
            with self.subTest(nums=nums):
                k, work = self.apply(nums)
                self.assertEqual(work[:k], brute_force(nums))

    def test_constraint_sized(self):
        rng = random.Random(801)
        nums = []
        value = -10 ** 4
        while len(nums) < 3 * 10 ** 4:
            nums.extend([value] * rng.randint(1, 4))
            value += 1
        nums = sorted(nums[:3 * 10 ** 4])
        self.assertEqual(len(nums), 3 * 10 ** 4)
        self.assertLessEqual(nums[-1], 10 ** 4)

        k, work = self.apply(nums)
        expected = brute_force(nums)
        self.assertEqual(k, len(expected))
        self.assertEqual(work[:k], expected)

    def test_constraint_sized_heavy_duplicates(self):
        nums = [5] * (3 * 10 ** 4)
        k, work = self.apply(nums)
        self.assertEqual(k, 2)
        self.assertEqual(work[:k], [5, 5])

        nums = list(range(3 * 10 ** 4))
        k, work = self.apply(nums)
        self.assertEqual(k, len(nums))
        self.assertEqual(work[:k], nums)


if __name__ == '__main__':
    unittest.main()
