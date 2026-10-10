"""Tests for 153. Find Minimum in Rotated Sorted Array.

Oracles, none of which is a binary search:

  - `min(nums)` and `sorted(nums)[0]`: brute force over the whole array;
  - `linear_rotation_min` walks the array until the value drops, i.e. it finds the
    rotation point by scanning rather than by halving;
  - `rotation_normalized_min` rebuilds the sorted array from the input by finding
    the rotation offset and returning its first element.

Every generated input is built the way the statement builds them: take a sorted
array of *distinct* values and rotate it between 1 and n times, so rotating n
times leaves it sorted. `read_count` additionally checks that the answer really is
found by halving -- a linear scan would blow the read budget on n = 5000.
"""

import itertools
import math
import random
import unittest

from _loader import load_solution

Solution = load_solution('153-find-minimum-in-rotated-sorted-array.py').Solution


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


def rotation_normalized_min(nums) -> int:
    offset = min(range(len(nums)), key=lambda index: nums[index])
    rebuilt = list(nums[offset:]) + list(nums[:offset])
    assert rebuilt == sorted(rebuilt)
    return rebuilt[0]


class CountingList(list):
    """A list that counts element reads, to bound the number of probes."""

    def __init__(self, values):
        super().__init__(values)
        self.reads = 0

    def __getitem__(self, index):
        self.reads += 1
        return super().__getitem__(index)


class FindMinimumInRotatedSortedArrayTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().findMin

    def assert_rotated(self, nums) -> int:
        expected = min(nums)
        result = self.solve(list(nums))
        self.assertEqual(result, expected, f'input {nums}')
        self.assertEqual(expected, sorted(nums)[0])
        self.assertEqual(expected, linear_rotation_min(nums))
        self.assertEqual(expected, rotation_normalized_min(nums))
        return result

    def test_official_examples(self):
        self.assertEqual(self.solve([3, 4, 5, 1, 2]), 1)
        self.assertEqual(self.solve([4, 5, 6, 7, 0, 1, 2]), 0)
        self.assertEqual(self.solve([11, 13, 15, 17]), 11)

    def test_single_element(self):
        self.assertEqual(self.solve([1]), 1)
        self.assertEqual(self.solve([-5000]), -5000)
        self.assertEqual(self.solve([5000]), 5000)

    def test_two_elements(self):
        self.assertEqual(self.solve([1, 2]), 1)
        self.assertEqual(self.solve([2, 1]), 1)
        self.assertEqual(self.solve([-1, -2]), -2)

    def test_minimum_at_every_position(self):
        base = [1, 2, 3, 4, 5, 6, 7]
        for rotation in range(1, len(base) + 1):
            nums = rotate(base, rotation)
            with self.subTest(rotation=rotation, nums=nums):
                self.assertEqual(self.solve(nums), 1)
                self.assert_rotated(nums)

    def test_fully_sorted_input_is_valid(self):
        # Rotating n times leaves the array sorted, which is still a valid input.
        nums = [0, 1, 2, 4, 5, 6, 7]
        self.assertEqual(self.solve(nums), 0)
        self.assertEqual(nums, sorted(nums))

    def test_boundary_values(self):
        self.assertEqual(self.solve([-5000, 5000]), -5000)
        self.assertEqual(self.solve([5000, -5000]), -5000)
        self.assertEqual(self.solve(rotate([-5000, -4999, 4999, 5000], 2)), -5000)

    def test_exhaustive_rotations_of_every_small_sorted_array(self):
        pool = list(range(-3, 4))  # seven distinct values
        cases = 0
        for size in range(1, 7):
            for combo in itertools.combinations(pool, size):
                for rotation in range(1, size + 1):
                    nums = rotate(list(combo), rotation)
                    with self.subTest(nums=nums):
                        self.assert_rotated(nums)
                    cases += 1
        self.assertEqual(cases, sum(math.comb(7, size) * size for size in range(1, 7)))

    def test_exhaustive_rotations_of_dense_ranges(self):
        for size in range(1, 9):
            base = list(range(size))
            for rotation in range(1, size + 1):
                nums = rotate(base, rotation)
                with self.subTest(nums=nums):
                    self.assertEqual(self.solve(nums), 0)

    def test_randomised_rotated_arrays(self):
        rng = random.Random(1530)
        for _ in range(300):
            size = rng.randint(1, 40)
            base = sorted(rng.sample(range(-60, 60), size))
            rotation = rng.randint(1, size)
            nums = rotate(base, rotation)
            with self.subTest(nums=nums):
                self.assert_rotated(nums)

    def test_randomised_wide_value_ranges(self):
        rng = random.Random(1531)
        for _ in range(100):
            size = rng.randint(2, 25)
            base = sorted(rng.sample(range(-5000, 5001), size))
            nums = rotate(base, rng.randint(1, size))
            with self.subTest(nums=nums):
                self.assert_rotated(nums)
                self.assertEqual(self.solve(nums), base[0])

    def test_logarithmic_number_of_probes(self):
        # n = 5000 is the constraint maximum; a scan-free answer needs about
        # 2 * log2(n) reads, a linear scan would need 5000.
        base = list(range(-2500, 2500))
        for rotation in (1, 2, 13, 2500, 4998, 4999, 5000):
            nums = CountingList(rotate(base, rotation))
            self.assertEqual(self.solve(nums), -2500)
            budget = 4 * math.ceil(math.log2(len(base))) + 8
            with self.subTest(rotation=rotation):
                self.assertLessEqual(nums.reads, budget)

    def test_constraint_sized(self):
        # n = 5000, the maximum, in several rotations.
        for rotation in (1, 2, 3, 2500, 4999, 5000):
            base = list(range(-2500, 2500))
            nums = rotate(base, rotation)
            with self.subTest(rotation=rotation):
                self.assertEqual(len(nums), 5000)
                self.assertEqual(self.solve(nums), -2500)
                self.assertEqual(self.solve(nums), min(nums))

    def test_constraint_sized_extreme_values(self):
        # Distinct values spread over the whole allowed range.
        base = list(range(-5000, 0))  # 5000 values, minimum -5000
        self.assertEqual(len(base), 5000)
        self.assertEqual(self.solve(rotate(base, 137)), -5000)
        self.assertEqual(self.solve(rotate(base, 5000)), -5000)

        high = list(range(0, 4999)) + [5000]  # 5000 values, minimum 0
        self.assertEqual(len(high), 5000)
        self.assertEqual(self.solve(rotate(high, 17)), 0)
        self.assertEqual(self.solve(rotate(high, 1)), 0)

        random_base = sorted(random.Random(1532).sample(range(-5000, 5001), 5000))
        nums = rotate(random_base, 137)
        self.assertEqual(self.solve(nums), random_base[0])
        self.assertEqual(self.solve(nums), min(nums))


if __name__ == '__main__':
    unittest.main()
