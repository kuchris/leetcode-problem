"""Tests for 154. Find Minimum in Rotated Sorted Array II.

Duplicates are the whole difficulty of this problem, so the sweep is exhaustive
over the input space rather than sampled: every multiset of size 1..7 over
{0, 1, 2}, every multiset of size 1..5 over {0, 1, 2, 3}, and every multiset of
size 1..5 over {-2, 0, 3}, each rotated 1..n times -- the only way the statement
builds an input.

Oracles, none of which is a binary search:

  - `min(nums)` and `sorted(nums)[0]`;
  - `linear_rotation_min` finds the rotation point by scanning and returns the
    element after the drop.

The read budget catches a regression to a linear scan on duplicate-free input,
while the all-equal arrays exercise the O(n) worst case the equality branch needs.
"""

import collections
import itertools
import math
import random
import unittest

from _loader import load_solution

Solution = load_solution('154-find-minimum-in-rotated-sorted-array-ii.py').Solution


def rotate(values, times: int) -> list:
    """Rotate left by `times` positions: one rotation moves the last to the front."""
    times %= len(values)
    if times == 0:
        return list(values)
    return list(values[-times:]) + list(values[:-times])


def linear_rotation_min(nums) -> int:
    for index in range(1, len(nums)):
        if nums[index] < nums[index - 1]:
            return nums[index]
    return nums[0]


class CountingList(list):
    """A list that counts element reads, to bound the number of probes."""

    def __init__(self, values):
        super().__init__(values)
        self.reads = 0

    def __getitem__(self, index):
        self.reads += 1
        return super().__getitem__(index)


class FindMinimumInRotatedSortedArrayTwoTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().findMin

    def assert_rotated(self, nums) -> int:
        expected = min(nums)
        result = self.solve(list(nums))
        self.assertEqual(result, expected, f'input {nums}')
        self.assertEqual(expected, sorted(nums)[0])
        self.assertEqual(expected, linear_rotation_min(nums))
        return result

    def test_official_examples(self):
        self.assertEqual(self.solve([1, 3, 5]), 1)
        self.assertEqual(self.solve([2, 2, 2, 0, 1]), 0)

    def test_single_element(self):
        for value in (-5000, -1, 0, 1, 5000):
            with self.subTest(value=value):
                self.assertEqual(self.solve([value]), value)

    def test_all_elements_equal(self):
        # The equality branch runs once per element here, so this is the O(n)
        # worst case -- and the answer is still the single value.
        for size in range(1, 21):
            with self.subTest(size=size):
                self.assertEqual(self.solve([7] * size), 7)
        self.assertEqual(self.solve([0] * 100), 0)
        self.assertEqual(self.solve([-5000] * 300), -5000)

    def test_duplicates_of_the_minimum(self):
        self.assertEqual(self.solve([1, 0, 0, 0, 1]), 0)
        self.assertEqual(self.solve([2, 2, 0, 0, 2, 2]), 0)
        self.assertEqual(self.solve([3, 3, 3, 1, 1, 1]), 1)
        self.assertEqual(self.solve([1, 1, 1, 3, 3, 3]), 1)

    def test_minimum_at_every_position_of_a_duplicated_array(self):
        base = [1, 1, 2, 2, 3, 3, 4, 4]
        for rotation in range(1, len(base) + 1):
            nums = rotate(base, rotation)
            with self.subTest(rotation=rotation, nums=nums):
                self.assertEqual(self.solve(nums), 1)
                self.assert_rotated(nums)

    def test_boundary_values(self):
        self.assertEqual(self.solve([-5000, 5000, 5000]), -5000)
        self.assertEqual(self.solve([5000, 5000, -5000]), -5000)
        self.assertEqual(self.solve([5000, 5000, 5000]), 5000)

    def test_exhaustive_multisets_over_three_values(self):
        cases = 0
        for size in range(1, 8):
            for multiset in itertools.combinations_with_replacement((0, 1, 2), size):
                for rotation in range(1, size + 1):
                    nums = rotate(list(multiset), rotation)
                    with self.subTest(nums=nums):
                        self.assert_rotated(nums)
                    cases += 1
        # Every multiset, every allowed rotation.
        self.assertEqual(cases, sum(math.comb(size + 2, 2) * size for size in range(1, 8)))

    def test_exhaustive_multisets_over_four_values(self):
        for size in range(1, 6):
            for multiset in itertools.combinations_with_replacement((0, 1, 2, 3), size):
                for rotation in range(1, size + 1):
                    nums = rotate(list(multiset), rotation)
                    with self.subTest(nums=nums):
                        self.assert_rotated(nums)

    def test_exhaustive_multisets_with_negative_values(self):
        for size in range(1, 6):
            for multiset in itertools.combinations_with_replacement((-2, 0, 3), size):
                for rotation in range(1, size + 1):
                    nums = rotate(list(multiset), rotation)
                    with self.subTest(nums=nums):
                        self.assert_rotated(nums)

    def test_exhaustive_equal_multisets(self):
        # [v] * n for every v and n is a rotation of itself, whatever the rotation.
        for value in (-1, 0, 1):
            for size in range(1, 7):
                for rotation in range(1, size + 1):
                    nums = rotate([value] * size, rotation)
                    with self.subTest(value=value, size=size, rotation=rotation):
                        self.assertEqual(nums, [value] * size)
                        self.assertEqual(self.solve(nums), value)

    def test_randomised_multisets(self):
        rng = random.Random(1540)
        for _ in range(400):
            size = rng.randint(1, 40)
            multiset = sorted(rng.choice((-3, -1, 0, 0, 1, 2, 2, 2)) for _ in range(size))
            nums = rotate(multiset, rng.randint(1, size))
            with self.subTest(nums=nums):
                self.assert_rotated(nums)
                self.assertEqual(self.solve(nums), multiset[0])

    def test_randomised_wide_values(self):
        rng = random.Random(1541)
        for _ in range(150):
            size = rng.randint(1, 30)
            multiset = sorted(rng.choice(range(-5000, 5001)) for _ in range(size))
            nums = rotate(multiset, rng.randint(1, size))
            with self.subTest(nums=nums):
                self.assert_rotated(nums)

    def test_logarithmic_probes_on_duplicate_free_input(self):
        # Without duplicates the equality branch never fires, so the search must
        # stay logarithmic; a scan would need 4000 reads.
        base = list(range(-2000, 2000))
        for rotation in (1, 3, 1000, 3999, 4000):
            nums = CountingList(rotate(base, rotation))
            self.assertEqual(self.solve(nums), -2000)
            budget = 4 * math.ceil(math.log2(len(base))) + 8
            with self.subTest(rotation=rotation):
                self.assertLessEqual(nums.reads, budget)

    def test_constraint_sized(self):
        # n = 5000, the constraint maximum.
        self.assertEqual(self.solve([2] * 4999 + [0]), 0)
        self.assertEqual(self.solve([0] + [2] * 4999), 0)
        self.assertEqual(self.solve([7] * 5000), 7)
        self.assertEqual(self.solve(list(range(-2500, 2500))), -2500)
        self.assertEqual(self.solve(rotate(list(range(-2500, 2500)), 4321)), -2500)

        rng = random.Random(1542)
        multiset = sorted(rng.choice((-5000, -5000, 0, 4999, 5000, 5000)) for _ in range(5000))
        nums = rotate(multiset, 1234)
        self.assertEqual(len(nums), 5000)
        self.assertEqual(self.solve(nums), multiset[0])
        self.assertEqual(self.solve(nums), min(nums))

    def test_constraint_sized_many_duplicates_of_the_minimum(self):
        multiset = sorted([0] * 1000 + [1] * 4000)
        for rotation in (1, 1000, 2500, 4000, 5000):
            nums = rotate(multiset, rotation)
            with self.subTest(rotation=rotation):
                self.assertEqual(len(nums), 5000)
                self.assertEqual(nums.count(0), 1000)
                self.assertEqual(self.solve(nums), 0)
                self.assertEqual(self.solve(nums), linear_rotation_min(nums))

    def test_constraint_sized_worst_case_reads(self):
        # All-equal input is allowed to cost O(n): the equality branch discards
        # one element per step, and the three-way comparison reads nums[mid] and
        # nums[high] twice each, so the bound is 4 reads per element.
        nums = CountingList([3] * 5000)
        self.assertEqual(self.solve(nums), 3)
        self.assertLessEqual(nums.reads, 4 * len(nums) + 8)


if __name__ == '__main__':
    unittest.main()
