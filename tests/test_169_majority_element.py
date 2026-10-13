"""Tests for 169. Majority Element.

Oracles, both different algorithms from the solution's single-pass voting:
  - ``Counter(nums).most_common(1)``, i.e. count everything and take the winner;
  - ``sorted(nums)[n // 2]``: with a strict majority the majority element is
    exactly the median, which needs no counting at all.

The problem guarantees that a majority element exists, so every generated input
is built that way (a value repeated more than n/2 times, plus filler that cannot
overtake it) instead of being sampled arbitrarily -- an array without a majority
would make the answer undefined rather than wrong.

Every answer is also checked against the definition directly: it must occur more
than n/2 times in the input. The O(1)-space follow-up is measured with
tracemalloc against the Counter oracle.
"""

import collections
import itertools
import random
import tracemalloc
import unittest

from _loader import load_solution

Solution = load_solution('169-majority-element.py').Solution


def counter_oracle(nums) -> int:
    return collections.Counter(nums).most_common(1)[0][0]


def median_oracle(nums) -> int:
    return sorted(nums)[len(nums) // 2]


def counts_as_majority(nums, value) -> bool:
    return nums.count(value) > len(nums) // 2


def array_with_majority(rng, length, majority, alphabet):
    """`length` values where `majority` is strictly more than half."""
    majority_count = length // 2 + 1
    filler = [rng.choice(alphabet) for _ in range(length - majority_count)]
    values = [majority] * majority_count + filler
    rng.shuffle(values)
    return values


def constraint_array(length: int) -> list:
    """A maximum-size array where 0 is the majority and the rest are distinct."""
    majority_count = length // 2 + 1
    filler_count = length - majority_count
    return [0] * majority_count + list(range(1, filler_count + 1))


class MajorityElementTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().majorityElement

    def check(self, nums):
        produced = self.solve(nums)
        self.assertTrue(counts_as_majority(nums, produced),
                        f'{produced} is not a majority of {nums}')
        self.assertEqual(produced, counter_oracle(nums))
        self.assertEqual(produced, median_oracle(nums))
        return produced

    def test_official_examples(self):
        self.assertEqual(self.solve([3, 2, 3]), 3)
        self.assertEqual(self.solve([2, 2, 1, 1, 1, 2, 2]), 2)
        self.assertEqual(self.check([3, 2, 3]), 3)
        self.assertEqual(self.check([2, 2, 1, 1, 1, 2, 2]), 2)

    def test_single_element(self):
        self.assertEqual(self.check([1]), 1)
        self.assertEqual(self.check([-10 ** 9]), -10 ** 9)
        self.assertEqual(self.check([10 ** 9]), 10 ** 9)

    def test_two_elements(self):
        # Only [x, x] can have a strict majority for n = 2.
        self.assertEqual(self.check([5, 5]), 5)
        self.assertEqual(self.check([-5, -5]), -5)

    def test_all_equal(self):
        self.assertEqual(self.check([7] * 100), 7)
        self.assertEqual(self.check([-10 ** 9] * 51), -10 ** 9)

    def test_boundary_values(self):
        self.assertEqual(self.check([10 ** 9, -10 ** 9, 10 ** 9]), 10 ** 9)
        self.assertEqual(self.check([-10 ** 9, 10 ** 9, -10 ** 9]), -10 ** 9)
        self.assertEqual(self.check([0, 0, 0, 1, 2]), 0)

    def test_adversarial_ordering(self):
        # The majority element arrives only at the end, after many cancellations.
        nums = [1, 2, 1, 2, 1, 2] + [3] * 7          # 3 occurs 7 > 6 of 13
        self.assertEqual(self.check(nums), 3)
        # Alternating distinct values before the majority arrives.
        nums = [1, 2, 3, 4] + [5] * 5                # 5 occurs 5 > 4 of 9
        self.assertEqual(self.check(nums), 5)
        # The majority is first, so the candidate must be replaced correctly.
        nums = [9] * 5 + [1, 2, 3, 4]
        self.assertEqual(self.check(nums), 9)

    def test_exhaustive_small_arrays(self):
        for length in range(1, 8):
            for values in itertools.product((1, 2), repeat=length):
                nums = list(values)
                if not counts_as_majority(nums, 1) and not counts_as_majority(nums, 2):
                    continue
                with self.subTest(nums=nums):
                    self.assertEqual(self.solve(nums), counter_oracle(nums))

    def test_exhaustive_three_value_arrays(self):
        for length in range(1, 7):
            for values in itertools.product((0, 1, 2), repeat=length):
                nums = list(values)
                if not any(counts_as_majority(nums, value) for value in (0, 1, 2)):
                    continue
                with self.subTest(nums=nums):
                    self.assertEqual(self.solve(nums), median_oracle(nums))

    def test_random_cases(self):
        rng = random.Random(1690)
        for _ in range(400):
            length = rng.randint(1, 200)
            majority = rng.randint(-10 ** 9, 10 ** 9)
            alphabet = [rng.randint(-10 ** 9, 10 ** 9) for _ in range(5)]
            nums = array_with_majority(rng, length, majority, alphabet)
            with self.subTest(length=length):
                self.check(nums)

    def test_random_narrow_alphabet(self):
        # A small alphabet makes the cancellations actually happen.
        rng = random.Random(1691)
        for _ in range(200):
            length = rng.randint(1, 500)
            majority = rng.randint(0, 2)
            nums = array_with_majority(rng, length, majority, [0, 1, 2])
            with self.subTest(length=length):
                self.assertEqual(self.solve(nums), counter_oracle(nums))

    def test_constraint_sized(self):
        # n = 5 * 10^4 is the constraint maximum.
        rng = random.Random(1692)
        length = 50_000
        nums = array_with_majority(rng, length, 999, list(range(10)))
        self.assertEqual(self.solve(nums), 999)
        self.assertEqual(self.solve(nums), counter_oracle(nums))

        # Half the array is distinct filler, so the majority is exactly n//2 + 1.
        nums = constraint_array(length)
        self.assertEqual(len(nums), length)
        self.assertEqual(self.solve(nums), 0)
        self.assertEqual(self.solve(nums), counter_oracle(nums))

        # All values equal.
        self.assertEqual(self.solve([10 ** 9] * length), 10 ** 9)

    def test_constant_space_against_the_counter_oracle(self):
        nums = constraint_array(50_000)
        self.assertEqual(len(nums), 50_000)

        tracemalloc.start()
        produced = self.solve(nums)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        self.assertEqual(produced, 0)

        tracemalloc.start()
        expected = counter_oracle(nums)
        _, oracle_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        self.assertEqual(expected, 0)

        # Voting keeps a candidate and a balance only; Counter builds a dict.
        self.assertLess(peak, 50_000)
        self.assertGreater(oracle_peak, 100_000)
        self.assertLess(peak, oracle_peak // 10)


if __name__ == '__main__':
    unittest.main()
