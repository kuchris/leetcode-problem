"""Tests for 101198. Longest Resilient Subarray I (Biweekly Contest 193, Q2).

Oracle: take the definition literally. For every subarray and every position in
it, delete that position and ask whether the remaining sum is divisible by k.
The lengths are then maximized by brute force, with no use of the "all elements
share one residue, lengths are 1 mod k / gcd(r, k)" characterization the solution
relies on -- so agreement is evidence, not a restatement.

Large inputs cannot be brute forced, so the constraint-sized tests use arrays
whose answer follows from the definition directly (all values divisible by k, or
a prime k larger than every possible remaining sum) plus one medium random case
that is still checked against the literal oracle.
"""

import itertools
import random
import unittest
from pathlib import Path

from _loader import load_solution

# Contest material is filed under contest/<contest name>/, not solutions/.
CONTEST_DIR = (
    Path(__file__).resolve().parents[1] / 'contest' / 'Biweekly Contest 193'
)
Solution = load_solution(
    'q2-longest-resilient-subarray-i.py', CONTEST_DIR
).Solution


def is_resilient(nums: list[int], start: int, stop: int, k: int) -> bool:
    """Literal definition: delete each position, test the rest of the window."""
    total = sum(nums[start:stop])
    return all((total - nums[i]) % k == 0 for i in range(start, stop))


def brute_force(nums: list[int], k: int) -> int:
    """Longest resilient subarray length, by literal enumeration."""
    best = 0
    for start in range(len(nums)):
        for stop in range(start + 1, len(nums) + 1):
            if stop - start > best and is_resilient(nums, start, stop, k):
                best = stop - start
    return best


def divisibility_scan(nums: list[int], k: int) -> int:
    """Independent O(n^2) scan for inputs too large for the literal oracle.

    Extends each window while its elements keep one residue and tests
    (m - 1) * r % k == 0 directly, without the gcd step the solution uses. Once
    a window mixes residues, every longer window from that start does too, so
    the scan stops there.
    """
    best = 1
    for start in range(len(nums)):
        residue = nums[start] % k
        total = 0
        for stop in range(start, len(nums)):
            value = nums[stop]
            if value % k != residue:
                break
            total += value
            length = stop - start + 1
            if length > best and (length - 1) * residue % k == 0:
                best = length
    return best


class LongestResilientSubarrayTests(unittest.TestCase):
    def assert_matches_oracle(self, nums: list[int], k: int):
        case = f'nums={nums}, k={k}'
        actual = Solution().resilientSubarray(list(nums), k)
        self.assertIsInstance(actual, int, case)
        self.assertEqual(actual, brute_force(nums, k), case)
        self.assertTrue(1 <= actual <= len(nums), f'{case}: {actual} out of range')

    def test_official_examples(self):
        self.assertEqual(Solution().resilientSubarray([2, 4, 6, 3], 2), 3)
        self.assertEqual(Solution().resilientSubarray([1, 4, 7, 1], 3), 4)
        self.assertEqual(Solution().resilientSubarray([5, 5, 4, 8], 4), 2)

    def test_single_element_is_always_resilient(self):
        for k in (1, 2, 5, 100000):
            with self.subTest(k=k):
                self.assertEqual(Solution().resilientSubarray([7], k), 1)
                self.assertEqual(Solution().resilientSubarray([100000], k), 1)

    def test_k_equal_to_one_makes_everything_resilient(self):
        self.assertEqual(Solution().resilientSubarray([7, 3, 9, 1], 1), 4)
        self.assertEqual(Solution().resilientSubarray([100000] * 2500, 1), 2500)

    def test_runs_of_multiples_of_k(self):
        # Every element divisible by k: S - a[i] stays divisible at any length.
        self.assertEqual(Solution().resilientSubarray([3, 3, 3], 3), 3)
        self.assertEqual(Solution().resilientSubarray([4, 8, 12, 16], 4), 4)
        self.assert_matches_oracle([4, 8, 16, 5, 4, 8], 4)

    def test_equal_values_limit_by_divisibility_of_length(self):
        # r = 1 mod k: length is valid iff (m - 1) * r is divisible by k.
        self.assertEqual(Solution().resilientSubarray([1, 1, 1], 2), 3)   # m - 1 = 2
        self.assertEqual(Solution().resilientSubarray([1, 1], 2), 1)      # m - 1 = 1
        self.assertEqual(Solution().resilientSubarray([5, 5], 4), 1)      # m - 1 = 1
        self.assertEqual(Solution().resilientSubarray([5] * 5, 4), 5)     # m - 1 = 4
        self.assertEqual(Solution().resilientSubarray([5] * 4, 4), 1)     # m - 1 = 3
        for k in range(1, 8):
            with self.subTest(k=k):
                self.assert_matches_oracle([5] * 6, k)

    def test_best_run_is_not_the_last_one(self):
        nums = [6, 2, 10, 3, 4, 7]
        self.assertEqual(Solution().resilientSubarray(nums, 4), 3)
        self.assert_matches_oracle(nums, 4)

    def test_exhaustive_small_inputs(self):
        values = [1, 2, 3, 4]
        for size in range(1, 5):
            for nums in itertools.product(values, repeat=size):
                for k in range(1, 8):
                    with self.subTest(nums=nums, k=k):
                        self.assert_matches_oracle(list(nums), k)

    def test_random_inputs(self):
        rng = random.Random(1932)
        for _ in range(1500):
            size = rng.randint(1, 14)
            nums = [rng.randint(1, 10) for _ in range(size)]
            k = rng.randint(1, 12)
            with self.subTest(nums=nums, k=k):
                self.assert_matches_oracle(nums, k)

    def test_random_medium_input_against_oracle(self):
        rng = random.Random(193_2)
        nums = [rng.randint(1, 20) for _ in range(150)]
        for k in (2, 3, 7, 10, 30):
            with self.subTest(k=k):
                self.assert_matches_oracle(nums, k)

    def test_constraint_sized_all_multiples(self):
        # Values are multiples of k, so every length is resilient: answer is n.
        nums = [2] * 2500
        self.assertEqual(Solution().resilientSubarray(nums, 2), 2500)
        self.assertEqual(Solution().resilientSubarray([100000] * 2500, 100000), 2500)

    def test_constraint_sized_prime_k_exceeds_reachable_sums(self):
        # Length m >= 2 needs (m - 1) * 1 divisible by the prime 99991 > 2499.
        nums = [1] * 2500
        self.assertEqual(Solution().resilientSubarray(nums, 99991), 1)

    def test_constraint_sized_repeating_residue(self):
        # k = 5, r = 1: valid lengths are 1, 6, 11, ...; the largest <= 2500 is 2496.
        nums = [1] * 2500
        self.assertEqual(Solution().resilientSubarray(nums, 5), 2496)
        self.assertEqual(Solution().resilientSubarray(nums[:2497], 5), 2496)
        self.assertEqual(Solution().resilientSubarray(nums[:2495], 5), 2491)

    def test_constraint_sized_random_mixed_input(self):
        # 2500 elements is the maximum length; the literal oracle is too slow,
        # so the independent divisibility scan is the authority here.
        rng = random.Random(193_3)
        for k in (2, 3, 17, 2500, 99991):
            with self.subTest(k=k):
                nums = [rng.randint(1, 100000) for _ in range(2500)]
                actual = Solution().resilientSubarray(list(nums), k)
                self.assertEqual(actual, divisibility_scan(nums, k))

    def test_constraint_sized_structured_inputs(self):
        rng = random.Random(193_4)
        # Long runs of one residue, padded with noise, at k values below and
        # above the run length.
        for k in (2, 4, 5, 7, 2500, 99991):
            for run in (3, 250, 2499, 2500):
                with self.subTest(k=k, run=run):
                    nums = [rng.randint(1, 100000) for _ in range(2500 - run)]
                    start = rng.randint(0, len(nums))
                    nums[start:start] = [(rng.randint(0, 99999) // k) * k + 1] * run
                    nums = nums[:2500]
                    actual = Solution().resilientSubarray(list(nums), k)
                    self.assertEqual(actual, divisibility_scan(nums, k))

    def test_input_not_mutated(self):
        nums = [2, 4, 6, 3]
        Solution().resilientSubarray(nums, 2)
        self.assertEqual(nums, [2, 4, 6, 3])


if __name__ == '__main__':
    unittest.main()
