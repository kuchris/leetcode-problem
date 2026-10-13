"""Tests for 164. Maximum Gap.

The solution must be linear, so the oracle is allowed to sort and the solution is
not: correctness is checked against `sorted()` on every small and random input,
while the linearity claim gets its own evidence --

  - a `builtins.sorted` patched to raise is installed around a call, so a
    solution that sorts through the builtin fails loudly;
  - the solution's source is scanned for `sorted(` / `.sort(` (they cannot be
    blocked otherwise, since `list.sort` is not patchable);
  - the pigeonhole parameters are re-derived for degenerate inputs and checked
    against the invariants that make bucketing valid: bucket size at least 1,
    `bucket_size * (n - 1) >= range`, and at most n buckets (so the bucket arrays
    cannot degenerate or replay the whole range).
"""

import builtins
import itertools
import random
import unittest

from _loader import SOLUTIONS_DIR, load_solution

Solution = load_solution('164-maximum-gap.py').Solution
SOLUTION_PATH = SOLUTIONS_DIR / '164-maximum-gap.py'


def sorted_oracle(nums: list[int]) -> int:
    if len(nums) < 2:
        return 0
    ordered = sorted(nums)
    return max(later - earlier for earlier, later in zip(ordered, ordered[1:]))


def bucket_parameters(nums: list[int]):
    """The bucket width and count the pigeonhole argument calls for."""
    size = len(nums)
    if size < 2:
        return 0, 0
    lowest, highest = min(nums), max(nums)
    if lowest == highest:
        return 0, 0
    bucket_size = max(1, -((lowest - highest) // (size - 1)))
    return bucket_size, (highest - lowest) // bucket_size + 1


class MaximumGapTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().maximumGap

    def test_official_examples(self):
        self.assertEqual(self.solve([3, 6, 9, 1]), 3)
        self.assertEqual(self.solve([10]), 0)

    def test_fewer_than_two_elements(self):
        for nums in ([0], [10 ** 9], [1], [5]):
            with self.subTest(nums=nums):
                self.assertEqual(self.solve(nums), 0)

    def test_all_values_equal(self):
        self.assertEqual(self.solve([7, 7, 7, 7]), 0)
        self.assertEqual(self.solve([0] * 100), 0)
        self.assertEqual(self.solve([10 ** 9] * 100), 0)

    def test_two_elements(self):
        self.assertEqual(self.solve([1, 3]), 2)
        self.assertEqual(self.solve([3, 1]), 2)
        self.assertEqual(self.solve([0, 10 ** 9]), 10 ** 9)
        self.assertEqual(self.solve([5, 5]), 0)

    def test_obvious_gap(self):
        self.assertEqual(self.solve([1, 2, 3, 100]), 97)
        self.assertEqual(self.solve([0, 10 ** 9, 1, 2]), 10 ** 9 - 2)

    def test_exhaustive_small_cases(self):
        for size in range(1, 7):
            for nums in itertools.product((0, 1, 2, 5), repeat=size):
                with self.subTest(nums=nums):
                    self.assertEqual(self.solve(list(nums)), sorted_oracle(list(nums)))

    def test_randomised_cases(self):
        rng = random.Random(1640)
        for _ in range(300):
            size = rng.randint(1, 200)
            nums = [rng.randint(0, 10 ** 9) for _ in range(size)]
            with self.subTest(size=size):
                self.assertEqual(self.solve(nums), sorted_oracle(nums))

    def test_randomised_small_alphabet(self):
        rng = random.Random(1641)
        for _ in range(200):
            size = rng.randint(2, 60)
            nums = [rng.choice([0, 1, 2, 10 ** 9, 10 ** 9 - 1]) for _ in range(size)]
            with self.subTest(size=size):
                self.assertEqual(self.solve(nums), sorted_oracle(nums))

    def test_bucket_parameters_cannot_degenerate(self):
        rng = random.Random(1642)
        size = 10 ** 5
        cases = {
            'all equal': [0] * size,
            'two extremes': [0, 10 ** 9],
            'three values': [0, 0, 10 ** 9],
            'dense range': list(range(size)),
            'one outlier': [0] * (size - 1) + [10 ** 9],
            'two clusters': [5] * (size - 2) + [0, 10 ** 9],
            'random': [rng.randint(0, 10 ** 9) for _ in range(size)],
            'all distinct sparse': [index * 10 ** 4 for index in range(size)],
        }
        for name, nums in cases.items():
            with self.subTest(case=name):
                low, high = min(nums), max(nums)
                bucket_size, bucket_count = bucket_parameters(nums)
                if len(nums) < 2 or low == high:
                    self.assertEqual((bucket_size, bucket_count), (0, 0))
                else:
                    self.assertGreaterEqual(bucket_size, 1)
                    self.assertGreaterEqual(bucket_size * (len(nums) - 1), high - low)
                    self.assertLessEqual(bucket_count, len(nums))
                    self.assertGreaterEqual(bucket_count, 1)
                self.assertEqual(self.solve(nums), sorted_oracle(nums))

    def test_does_not_call_the_sorted_builtin(self):
        saved = builtins.sorted

        def forbidden(*args, **kwargs):
            raise AssertionError('sorted() is not allowed: the solution must be linear')

        builtins.sorted = forbidden
        try:
            self.assertEqual(self.solve([3, 6, 9, 1]), 3)
            self.assertEqual(self.solve([1, 100, 3, 200, 5, 10 ** 9]), 10 ** 9 - 200)
            self.assertEqual(self.solve([0] * 50), 0)
        finally:
            builtins.sorted = saved

    def test_source_contains_no_sort_call(self):
        source = SOLUTION_PATH.read_text(encoding='utf-8')
        body = source.split('class Solution', 1)[1]
        self.assertNotIn('sorted(', body)
        self.assertNotIn('.sort(', body)

    def test_constraint_sized(self):
        # 10^5 elements is the constraint maximum, values up to 10^9.
        rng = random.Random(1643)
        size = 10 ** 5

        random_values = [rng.randint(0, 10 ** 9) for _ in range(size)]
        self.assertEqual(self.solve(random_values), sorted_oracle(random_values))

        progression = [index * (10 ** 9 // size) for index in range(size)]
        self.assertEqual(self.solve(progression), 10 ** 9 // size)

        with_one_huge_gap = [rng.randint(0, 1000) for _ in range(size - 1)] + [10 ** 9]
        self.assertEqual(self.solve(with_one_huge_gap), sorted_oracle(with_one_huge_gap))

        self.assertEqual(self.solve([10 ** 9] * size), 0)
        self.assertEqual(self.solve([0] * (size - 1) + [10 ** 9]), 10 ** 9)
        self.assertEqual(self.solve(list(range(size))), 1)
        self.assertEqual(self.solve(list(range(size))[::-1]), 1)


if __name__ == '__main__':
    unittest.main()
