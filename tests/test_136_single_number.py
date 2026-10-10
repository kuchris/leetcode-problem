"""Tests for 136. Single Number.

Two oracles, neither of them a fold with XOR:

  - `counter_oracle` counts occurrences and returns the value seen once;
  - `sum_oracle` uses 2 * sum(set(nums)) - sum(nums), which is exact precisely
    because every other value appears exactly twice.

The generated inputs always satisfy the stated guarantee: a set of values is
doubled and one value outside that set is added once, so nothing here relies on
an input the problem excludes.
"""

import itertools
import random
import unittest
from collections import Counter

from _loader import load_solution

Solution = load_solution('136-single-number.py').Solution


def counter_oracle(nums: list[int]) -> int:
    counts = Counter(nums)
    for value, count in counts.items():
        if count == 1:
            return value
    raise AssertionError('no value appears exactly once')


def sum_oracle(nums: list[int]) -> int:
    return 2 * sum(set(nums)) - sum(nums)


def doubled_arrays(pool):
    """Arrays = two copies of a subset of `pool` plus one value outside it."""
    for size in range(len(pool) + 1):
        for chosen in itertools.combinations(pool, size):
            for single in pool:
                if single in chosen:
                    continue
                yield list(chosen) * 2 + [single]


class SingleNumberTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().singleNumber

    def check(self, nums, expected):
        self.assertEqual(self.solve(nums), expected)
        self.assertEqual(counter_oracle(nums), expected)
        self.assertEqual(sum_oracle(nums), expected)

    def test_official_examples(self):
        self.check([2, 2, 1], 1)
        self.check([4, 1, 2, 1, 2], 4)
        self.check([1], 1)

    def test_single_element(self):
        for value in (0, 1, -1, 3 * 10 ** 4, -3 * 10 ** 4):
            with self.subTest(value=value):
                self.check([value], value)

    def test_zero_and_negative_values(self):
        self.check([0, 0, -7], -7)
        self.check([-1, -1, -2, -2, 0], 0)
        self.check([-3 * 10 ** 4, 3 * 10 ** 4, -3 * 10 ** 4, 3 * 10 ** 4, -1], -1)

    def test_boundary_values(self):
        self.check([3 * 10 ** 4, 3 * 10 ** 4, -3 * 10 ** 4], -3 * 10 ** 4)
        self.check([-3 * 10 ** 4, -3 * 10 ** 4, 3 * 10 ** 4], 3 * 10 ** 4)

    def test_pairs_are_cancelled_whatever_the_order(self):
        self.check([1, 2, 1, 2, 9], 9)
        self.check([9, 1, 2, 1, 2], 9)
        self.check([2, 1, 2, 1, 9], 9)

    def test_exhaustive_small_cases(self):
        for pool in ([0, 1], [0, 1, 2], [0, 1, 2, 3], [0, -1, 2, -3, 4]):
            for nums in doubled_arrays(pool):
                with self.subTest(nums=nums):
                    expected = counter_oracle(nums)
                    self.assertEqual(self.solve(nums), expected)
                    self.assertEqual(sum_oracle(nums), expected)

    def test_exhaustive_small_cases_with_permutations(self):
        # Pool of three keeps the arrays short (at most 7 elements), so every
        # permutation of every generated array stays cheap to check.
        for nums in doubled_arrays([0, 1, 2]):
            expected = counter_oracle(nums)
            for permutation in itertools.permutations(nums):
                with self.subTest(nums=permutation):
                    self.assertEqual(self.solve(list(permutation)), expected)

    def test_randomised_cases(self):
        rng = random.Random(1360)
        for _ in range(300):
            pool = rng.sample(range(-3 * 10 ** 4, 3 * 10 ** 4 + 1), rng.randint(1, 40))
            single = rng.choice(pool)
            nums = [value for value in pool if value != single] * 2 + [single]
            rng.shuffle(nums)
            with self.subTest(size=len(nums)):
                expected = counter_oracle(nums)
                self.assertEqual(self.solve(nums), expected)
                self.assertEqual(sum_oracle(nums), expected)

    def test_constraint_sized(self):
        # The length of a valid array is always odd (2k + 1), so the largest
        # legal size below 3 * 10^4 is 29999.
        values = list(range(-14999, 0))
        nums = values * 2 + [3 * 10 ** 4]
        self.assertEqual(len(nums), 29999)
        self.assertLessEqual(len(nums), 3 * 10 ** 4)
        self.check(nums, 3 * 10 ** 4)

        rng = random.Random(1361)
        pool = rng.sample(range(-3 * 10 ** 4, 3 * 10 ** 4 + 1), 14999)
        nums = pool * 2 + [-1]
        rng.shuffle(nums)
        self.assertEqual(len(nums), 29999)
        self.assertEqual(self.solve(nums), -1)

        nums = list(range(1, 15000)) * 2 + [0]
        self.assertEqual(self.solve(nums), 0)


if __name__ == '__main__':
    unittest.main()
