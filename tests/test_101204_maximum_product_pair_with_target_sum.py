"""Tests for 101204. Maximum Product Pair With Target Sum (Biweekly Contest 193, Q1).

Oracle: enumerate every ordered pair of distinct indices, keep the valid ones
(sum == target and nums[i] > nums[j]) and take the largest product directly.
That brute force follows the statement literally instead of the parabola
argument the solution uses, so agreement between them is evidence rather than a
restatement.

The statement allows any pair that attains the maximum product, so the check is:
the returned pair is valid and its product equals the oracle's maximum product.
A separate test pins the exact index pairs of the three official examples,
where the maximizing pair happens to be unique.
"""

import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('101204-maximum-product-pair-with-target-sum.py').Solution

NO_PAIR = [-1, -1]


def brute_force(nums: list[int], target: int):
    """Maximum product over valid pairs, or None when no valid pair exists."""
    best_product = None
    for i, j in itertools.permutations(range(len(nums)), 2):
        if nums[i] + nums[j] == target and nums[i] > nums[j]:
            product = nums[i] * nums[j]
            if best_product is None or product > best_product:
                best_product = product
    return best_product


class MaximumProductPairTests(unittest.TestCase):
    def assert_matches_oracle(self, nums: list[int], target: int):
        expected = brute_force(nums, target)
        actual = Solution().maxProductPair(list(nums), target)
        case = f'nums={nums}, target={target}'
        self.assertIsInstance(actual, list, case)
        self.assertEqual(len(actual), 2, case)
        i, j = actual
        if expected is None:
            self.assertEqual(actual, NO_PAIR, case)
            return
        self.assertNotEqual(actual, NO_PAIR, case)
        for index in (i, j):
            self.assertIsInstance(index, int, case)
            self.assertTrue(0 <= index < len(nums), f'{case}: index {index} out of range')
        self.assertNotEqual(i, j, f'{case}: indices must be distinct')
        self.assertEqual(nums[i] + nums[j], target, f'{case}: sum mismatch')
        self.assertGreater(nums[i], nums[j], f'{case}: nums[i] > nums[j] required')
        self.assertEqual(nums[i] * nums[j], expected, f'{case}: product not maximal')

    def test_official_examples(self):
        # The maximizing pair is unique in each example, so indices are pinned.
        self.assertEqual(Solution().maxProductPair([1, 2, 3, 4], 5), [2, 1])
        self.assertEqual(Solution().maxProductPair([-3, -1, 4, 2], 1), [3, 1])
        self.assertEqual(Solution().maxProductPair([3, 3, 5], 6), NO_PAIR)

    def test_no_valid_pair_cases(self):
        self.assertEqual(Solution().maxProductPair([2, 2], 4), NO_PAIR)       # equal values
        self.assertEqual(Solution().maxProductPair([1, 2], 10), NO_PAIR)      # complement absent
        self.assertEqual(Solution().maxProductPair([0, 0, 0], 0), NO_PAIR)    # never nums[i] > nums[j]
        self.assertEqual(Solution().maxProductPair([-1, -1], -2), NO_PAIR)
        self.assertEqual(Solution().maxProductPair([-100, 100], 100), NO_PAIR)  # complement 0 absent

    def test_size_two_boundaries(self):
        self.assertEqual(Solution().maxProductPair([1, 5], 6), [1, 0])
        self.assertEqual(Solution().maxProductPair([5, 1], 6), [0, 1])
        # 100 + (-100) == 0 with 100 > -100, so the pair is valid either way round.
        self.assertEqual(Solution().maxProductPair([-100, 100], 0), [1, 0])
        self.assertEqual(Solution().maxProductPair([100, -100], 0), [0, 1])
        self.assertEqual(Solution().maxProductPair([-100, 0], -100), [1, 0])
        self.assert_matches_oracle([-100, -100], -200)

    def test_picks_value_closest_to_half_target(self):
        # Complement of every x below is present, so the parabola argument makes
        # the smallest x above target / 2 the winner (4 * 3 = 12 > 5 * 2 = 10).
        nums = [3, 2, 4, 5, -7, 6]
        self.assertEqual(Solution().maxProductPair(nums, 7), [2, 0])
        self.assert_matches_oracle(nums, 7)

    def test_duplicate_values_use_distinct_indices(self):
        actual = Solution().maxProductPair([3, 3, 1, 1], 4)
        self.assert_matches_oracle([3, 3, 1, 1], 4)
        self.assertNotEqual(actual[0], actual[1])

    def test_exhaustive_small_inputs(self):
        values = [-3, -2, -1, 0, 1, 2, 3]
        targets = range(-6, 8)
        for size in (2, 3):
            for nums in itertools.product(values, repeat=size):
                for target in targets:
                    with self.subTest(nums=nums, target=target):
                        self.assert_matches_oracle(list(nums), target)

    def test_random_inputs(self):
        rng = random.Random(193)
        for _ in range(2000):
            size = rng.randint(2, 8)
            nums = [rng.randint(-6, 6) for _ in range(size)]
            target = rng.randint(-10, 10)
            with self.subTest(nums=nums, target=target):
                self.assert_matches_oracle(nums, target)

    def test_constraint_sized_input(self):
        nums = list(range(-50, 50))  # 100 values, the maximum length
        for target in (0, 7, -7, 1, -1):
            with self.subTest(target=target):
                self.assert_matches_oracle(nums, target)

    def test_constraint_sized_negative_heavy_input(self):
        rng = random.Random(193_1)
        nums = [rng.randint(-100, 0) for _ in range(100)]
        for target in (-100, -50, 0, -1):
            with self.subTest(target=target):
                self.assert_matches_oracle(nums, target)

    def test_input_not_mutated(self):
        nums = [4, 1, 3, 2]
        Solution().maxProductPair(nums, 5)
        self.assertEqual(nums, [4, 1, 3, 2])


if __name__ == '__main__':
    unittest.main()
