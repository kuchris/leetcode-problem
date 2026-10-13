"""Tests for 162. Find Peak Element.

The statement accepts any peak, so the oracle enumerates *all* peak indices
(elements strictly greater than both neighbours, with the array's ends treated as
-infinity) and the tests assert only that the returned index is one of them. A
second, definition-level check re-derives the two comparisons from the returned
index itself, which catches a solution that returns an out-of-range index or a
non-peak even when the peak set is large.

Every generated array respects the guarantee nums[i] != nums[i + 1].
"""

import random
import unittest

from _loader import load_solution

Solution = load_solution('162-find-peak-element.py').Solution


def peak_indices(nums: list[int]) -> list[int]:
    """Every index that is strictly greater than its existing neighbours."""
    n = len(nums)
    return [index for index in range(n)
            if (index == 0 or nums[index] > nums[index - 1])
            and (index == n - 1 or nums[index] > nums[index + 1])]


def is_peak(nums: list[int], index: int) -> bool:
    """Definitional check of one index, with -infinity outside the array."""
    if not 0 <= index < len(nums):
        return False
    if index > 0 and nums[index] <= nums[index - 1]:
        return False
    if index < len(nums) - 1 and nums[index] <= nums[index + 1]:
        return False
    return True


def adjacent_distinct_arrays(alphabet, size: int):
    """Every array of `size` values from `alphabet` with no equal neighbours."""
    if size == 0:
        return
    for first in alphabet:
        partials = [(first,)]
        for _ in range(size - 1):
            combined = []
            for partial in partials:
                for value in alphabet:
                    if value != partial[-1]:
                        combined.append(partial + (value,))
            partials = combined
        yield from partials


class FindPeakElementTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().findPeakElement

    def assert_is_peak(self, nums):
        index = self.solve(list(nums))
        self.assertTrue(is_peak(nums, index),
                        f'index {index} is not a peak of {nums[:20]}')
        self.assertIn(index, peak_indices(nums))
        return index

    def test_official_examples(self):
        self.assertEqual(self.solve([1, 2, 3, 1]), 2)
        self.assertIn(self.solve([1, 2, 1, 3, 5, 6, 4]), peak_indices([1, 2, 1, 3, 5, 6, 4]))

    def test_single_element(self):
        self.assertEqual(self.solve([0]), 0)
        self.assertEqual(self.solve([-2 ** 31]), 0)
        self.assertEqual(self.solve([2 ** 31 - 1]), 0)

    def test_two_elements(self):
        self.assertEqual(self.solve([1, 2]), 1)
        self.assertEqual(self.solve([2, 1]), 0)
        self.assertEqual(self.solve([-2 ** 31, 2 ** 31 - 1]), 1)
        self.assertEqual(self.solve([2 ** 31 - 1, -2 ** 31]), 0)

    def test_monotone_arrays(self):
        increasing = list(range(10))
        decreasing = list(range(9, -1, -1))
        self.assertEqual(self.solve(increasing), len(increasing) - 1)
        self.assertEqual(self.solve(decreasing), 0)

    def test_boundary_values(self):
        self.assert_is_peak([-2 ** 31, 2 ** 31 - 1, -2 ** 31])
        self.assert_is_peak([0, 2 ** 31 - 1, 0, -2 ** 31, 0])

    def test_exhaustive_small_cases(self):
        for size in range(1, 8):
            for nums in adjacent_distinct_arrays((0, 1, 2), size):
                with self.subTest(nums=nums):
                    self.assert_is_peak(list(nums))

    def test_exhaustive_small_cases_four_values(self):
        for size in range(1, 6):
            for nums in adjacent_distinct_arrays((0, 1, 2, 3), size):
                with self.subTest(nums=nums):
                    self.assert_is_peak(list(nums))

    def test_randomised_cases(self):
        rng = random.Random(1620)
        for _ in range(300):
            size = rng.randint(1, 200)
            nums = [rng.randint(-2 ** 31, 2 ** 31 - 1) for _ in range(size)]
            for index in range(1, size):
                if nums[index] == nums[index - 1]:
                    nums[index] = nums[index - 1] + 1 if nums[index - 1] < 2 ** 31 - 1 \
                        else nums[index - 1] - 1
            with self.subTest(size=size):
                self.assert_is_peak(nums)

    def test_randomised_mountain_and_zigzag(self):
        rng = random.Random(1621)
        for _ in range(100):
            size = rng.randint(2, 300)
            peak = rng.randrange(size)
            nums = []
            for index in range(size):
                nums.append(abs(index - peak))
            for index in range(1, size):
                if nums[index] == nums[index - 1]:
                    nums[index] += 1
            with self.subTest(size=size, peak=peak):
                self.assert_is_peak(nums)

            zigzag = [0 if index % 2 == 0 else -1 for index in range(size)]
            self.assert_is_peak(zigzag)

    def test_constraint_sized(self):
        # 1000 elements is the constraint maximum.
        size = 1000

        increasing = list(range(size))
        self.assertEqual(self.solve(increasing), size - 1)
        decreasing = list(range(size, 0, -1))
        self.assertEqual(self.solve(decreasing), 0)

        mountain = list(range(size // 2)) + list(range(size - size // 2, 0, -1))
        index = self.assert_is_peak(mountain)
        self.assertIn(index, (size // 2 - 1, size // 2))

        for pattern in ([0, 1], [0, -1], [-2 ** 31, 2 ** 31 - 1]):
            nums = [pattern[index % 2] for index in range(size)]
            if nums[0] == nums[1]:
                nums[1] += 1
            with self.subTest(pattern=pattern):
                self.assert_is_peak(nums)

        rng = random.Random(1622)
        nums = [rng.randint(-2 ** 31, 2 ** 31 - 1) for _ in range(size)]
        while any(nums[index] == nums[index + 1] for index in range(size - 1)):
            for index in range(size - 1):
                if nums[index] == nums[index + 1]:
                    nums[index + 1] = nums[index + 1] + 1 if nums[index + 1] < 2 ** 31 - 1 \
                        else nums[index + 1] - 1
        self.assert_is_peak(nums)


if __name__ == '__main__':
    unittest.main()
