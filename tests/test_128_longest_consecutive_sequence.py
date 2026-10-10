"""Tests for 128. Longest Consecutive Sequence.

Two independent oracles:

  - `sorted_scan` sorts the distinct values and measures the longest run of
    consecutive integers -- no hashing at all, O(n log n).
  - `union_find` unions every value with value + 1 when both are present and
    reports the largest component -- a completely different data structure from
    both the solution and the sorted scan.

The exhaustive sweep enumerates every multiset of up to four values drawn from a
five-value window, which is where duplicates, negative values and gaps interact.
"""

import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('128-longest-consecutive-sequence.py').Solution


def sorted_scan(nums) -> int:
    values = sorted(set(nums))
    best = 0
    run = 0
    previous = None
    for value in values:
        run = run + 1 if previous is not None and value == previous + 1 else 1
        best = max(best, run)
        previous = value
    return best


def union_find(nums) -> int:
    parent = {value: value for value in nums}
    size = {value: 1 for value in nums}

    def find(value):
        root = value
        while parent[root] != root:
            root = parent[root]
        while parent[value] != root:  # path compression
            parent[value], value = root, parent[value]
        return root

    best = 0
    for value in parent:
        if value + 1 in parent:
            left, right = find(value), find(value + 1)
            if left != right:
                parent[right] = left
                size[left] += size[right]
        best = max(best, size[find(value)])
    return best


class LongestConsecutiveSequenceTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().longestConsecutive

    def test_official_examples(self):
        self.assertEqual(self.solve([100, 4, 200, 1, 3, 2]), 4)
        self.assertEqual(self.solve([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]), 9)
        self.assertEqual(self.solve([1, 0, 1, 2]), 3)

    def test_empty_and_single(self):
        self.assertEqual(self.solve([]), 0)
        self.assertEqual(self.solve([7]), 1)
        self.assertEqual(self.solve([-10 ** 9]), 1)
        self.assertEqual(self.solve([10 ** 9]), 1)

    def test_duplicates_do_not_extend_runs(self):
        self.assertEqual(self.solve([1, 1, 1, 1]), 1)
        self.assertEqual(self.solve([5, 5, 4, 4, 3]), 3)
        self.assertEqual(self.solve([2, 2, 3, 3, 4, 4]), 3)

    def test_negative_and_boundary_values(self):
        self.assertEqual(self.solve([-3, -2, -1, 0, 1]), 5)
        self.assertEqual(self.solve([-10 ** 9, -10 ** 9 + 1, 10 ** 9 - 1, 10 ** 9]), 2)
        self.assertEqual(self.solve([-1, 0, 1, 1, 2]), 4)
        self.assertEqual(self.solve([-1, 0, 2, 3]), 2)

    def test_gaps_choose_the_longest_run(self):
        self.assertEqual(self.solve([1, 2, 3, 10, 11, 12, 13]), 4)
        self.assertEqual(self.solve([1, 3, 5, 7, 9]), 1)
        self.assertEqual(self.solve(list(range(0, 10)) + list(range(20, 26))), 10)

    def test_exhaustive_small_multisets(self):
        for length in range(0, 5):
            for nums in itertools.product(range(-2, 3), repeat=length):
                nums = list(nums)
                with self.subTest(nums=nums):
                    expected = sorted_scan(nums)
                    self.assertEqual(self.solve(nums), expected)
                    self.assertEqual(expected, union_find(nums))

    def test_exhaustive_small_permutations(self):
        # Every ordering of the same window exposes any dependence on input order.
        for nums in itertools.permutations(range(-1, 4)):
            with self.subTest(nums=nums):
                self.assertEqual(self.solve(list(nums)), 5)

    def test_randomised_against_both_oracles(self):
        rng = random.Random(1280)
        for _ in range(300):
            nums = [rng.randint(-30, 30) for _ in range(rng.randint(0, 40))]
            with self.subTest(nums=nums):
                expected = sorted_scan(nums)
                self.assertEqual(self.solve(nums), expected)
                self.assertEqual(expected, union_find(nums))

    def test_randomised_sparse_against_both_oracles(self):
        rng = random.Random(1281)
        for _ in range(200):
            nums = [rng.randint(-10 ** 9, 10 ** 9) for _ in range(rng.randint(0, 30))]
            with self.subTest(nums=nums):
                expected = sorted_scan(nums)
                self.assertEqual(self.solve(nums), expected)
                self.assertEqual(expected, union_find(nums))

    def test_constraint_sized_full_range(self):
        # 10^5 values forming one run of 10^5.
        nums = list(range(10 ** 5))
        random.Random(1282).shuffle(nums)
        self.assertEqual(self.solve(nums), 10 ** 5)

    def test_constraint_sized_full_range_descending(self):
        self.assertEqual(self.solve(list(range(10 ** 5, 0, -1))), 10 ** 5)

    def test_constraint_sized_sparse(self):
        rng = random.Random(1283)
        nums = [rng.randint(-10 ** 9, 10 ** 9) for _ in range(10 ** 5)]
        self.assertEqual(self.solve(nums), sorted_scan(nums))

    def test_constraint_sized_blocks(self):
        rng = random.Random(1284)
        nums = []
        for start in range(0, 10 ** 5, 7):
            nums.extend(range(start, start + 3))
        rng.shuffle(nums)
        self.assertEqual(self.solve(nums), 3)

    def test_constraint_sized_duplicates(self):
        rng = random.Random(1285)
        nums = [rng.randint(0, 50) for _ in range(10 ** 5)]
        self.assertEqual(self.solve(nums), sorted_scan(nums))
        self.assertEqual(self.solve(nums), 51)

    def test_constraint_sized_boundary_extremes(self):
        span = [10 ** 9 - 5, -10 ** 9, 10 ** 9, -10 ** 9 + 1, 10 ** 9 - 1, -10 ** 9 + 2]
        nums = span + [0] * (10 ** 5 - len(span))
        self.assertEqual(self.solve(nums), 3)


if __name__ == '__main__':
    unittest.main()
