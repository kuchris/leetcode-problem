"""Tests for 179. Largest Number.

Oracles:
  - ``permutation_oracle``: every permutation of the string forms, take the
    largest concatenation, then strip leading zeros. The definition, with no
    comparator and no transitivity assumption.
  - ``repeat_oracle``: sorts the string forms by their *infinite repetition*
    (each form repeated and truncated) — a standard alternative characterisation
    of the same order (``a + b > b + a`` exactly when the endless repetition of
    ``a`` exceeds that of ``b``) that never compares a pair directly. It is the
    oracle for the 100-element constraint cases where permutations are hopeless.
  - structural checks: the answer must use exactly the input's digits, must have
    no leading zero unless every number is zero, and must be no longer than the
    input's digits.

Exhaustive sweep: every sequence of length 1..4 over {0, 1, 10, 12, 121, 9}
(an alphabet full of comparator traps) and every sequence of length 5..6 over
{1, 12, 121}.
"""

import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('179-largest-number.py').Solution

MAX_COUNT = 100
MAX_VALUE = 10 ** 9


def permutation_oracle(nums) -> str:
    texts = [str(num) for num in nums]
    best = max(''.join(order) for order in itertools.permutations(texts))
    return best.lstrip('0') or '0'


def repeat_oracle(nums) -> str:
    """Sort by the truncated endless repetition of each string form."""
    texts = [str(num) for num in nums]
    length = 2 * max(len(text) for text in texts)
    keyed = sorted(
        texts,
        key=lambda text: (text * (length // len(text) + 1))[:length],
        reverse=True,
    )
    return ''.join(keyed).lstrip('0') or '0'


def structural_errors(nums, result) -> list:
    """Properties the answer must have, independent of any ordering oracle."""
    problems = []
    texts = [str(num) for num in nums]
    if all(text == '0' for text in texts):
        # The only case where stripping zeros removes digits: the answer is "0".
        if result != '0':
            problems.append('an all-zero input must answer exactly "0"')
        return problems
    if sorted(result) != sorted(''.join(texts)):
        problems.append('the answer does not use exactly the input digits')
    if len(result) > sum(len(text) for text in texts):
        problems.append('the answer is longer than the input digits')
    if result[0] == '0':
        problems.append('the answer has a leading zero')
    if set(result) == {'0'}:
        problems.append('a non-zero input cannot answer "0"')
    return problems


class LargestNumberTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().largestNumber

    def check(self, nums):
        result = self.solve(list(nums))
        self.assertEqual(result, permutation_oracle(nums))
        self.assertEqual(result, repeat_oracle(nums))
        self.assertEqual(structural_errors(nums, result), [])
        return result

    def test_official_examples(self):
        self.assertEqual(self.solve([10, 2]), "210")
        self.assertEqual(self.solve([3, 30, 34, 5, 9]), "9534330")
        self.check([10, 2])
        self.check([3, 30, 34, 5, 9])

    def test_all_zero_inputs_answer_zero(self):
        for count in (1, 2, 3, 5, 10):
            with self.subTest(count=count):
                self.assertEqual(self.solve([0] * count), "0")

    def test_single_element(self):
        self.assertEqual(self.solve([0]), "0")
        self.assertEqual(self.solve([7]), "7")
        self.assertEqual(self.solve([MAX_VALUE]), "1000000000")

    def test_comparator_traps(self):
        # 121 must follow 12: "12121" beats "12112".
        self.assertEqual(self.solve([121, 12]), "12121")
        # 3 must precede 30: "330" beats "303".
        self.assertEqual(self.solve([3, 30]), "330")
        self.assertEqual(self.solve([30, 3]), "330")
        # Leading zeros are dropped only when nothing else is there.
        self.assertEqual(self.solve([1, 0]), "10")
        self.assertEqual(self.solve([0, 1]), "10")
        self.assertEqual(self.solve([1, 10, 100]), "110100")
        self.assertEqual(self.solve([0, 0, 1]), "100")
        self.check([121, 12])
        self.check([3, 30])
        self.check([0, 0, 1])

    def test_boundary_values(self):
        self.assertEqual(self.solve([MAX_VALUE, 999999999]), "999999999" + "1000000000")
        self.check([MAX_VALUE, 999999999])
        self.check([MAX_VALUE, 1])
        self.check([0, MAX_VALUE, 0])

    def test_exhaustive_short_sequences(self):
        alphabet = (0, 1, 10, 12, 121, 9)
        for length in range(1, 5):
            for nums in itertools.product(alphabet, repeat=length):
                with self.subTest(nums=nums):
                    self.check(list(nums))
        trap = (1, 12, 121)
        for length in (5, 6):
            for nums in itertools.product(trap, repeat=length):
                with self.subTest(nums=nums):
                    self.check(list(nums))

    def test_random_lists_against_permutations(self):
        rng = random.Random(1790)
        values = [0, 1, 2, 9, 10, 11, 12, 98, 99, 100, 1000,
                  999999999, MAX_VALUE]
        for _ in range(300):
            length = rng.randint(1, 8)
            nums = [rng.choice(values) for _ in range(length)]
            with self.subTest(nums=nums):
                self.check(nums)

    def test_medium_list_against_permutations(self):
        # 8! = 40320 permutations is still brute-forceable.
        rng = random.Random(1791)
        for _ in range(20):
            nums = [rng.choice([0, 1, 9, 12, 121, 999, MAX_VALUE])
                    for _ in range(8)]
            with self.subTest(nums=nums):
                self.check(nums)

    def test_constraint_sized(self):
        rng = random.Random(1792)
        # The stated maximum: 100 numbers, the largest allowed values included.
        nums = [rng.choice([0, 1, 9, 12, 121, 1000000, 999999999, MAX_VALUE])
                for _ in range(MAX_COUNT)]
        result = self.solve(list(nums))
        self.assertEqual(result, repeat_oracle(nums))
        self.assertEqual(structural_errors(nums, result), [])
        self.assertEqual(len(result), sum(len(str(num)) for num in nums))

        # All zeros at the constraint size, and a single non-zero among them.
        self.assertEqual(self.solve([0] * MAX_COUNT), "0")
        zeros_with_one = [0] * (MAX_COUNT - 1) + [1]
        self.assertEqual(self.solve(zeros_with_one), "1" + "0" * (MAX_COUNT - 1))
        self.assertEqual(self.solve(zeros_with_one), repeat_oracle(zeros_with_one))

        # All maximum values.
        self.assertEqual(self.solve([MAX_VALUE] * MAX_COUNT),
                         "1000000000" * MAX_COUNT)

        # Values that are prefixes of one another at the constraint size.
        self.assertEqual(
            self.solve([9, 99, 999, 9999, 99999, 999999, 9999999, 99999999,
                        999999999, MAX_VALUE]),
            "999999999" + "99999999" + "9999999" + "999999" + "99999"
            + "9999" + "999" + "99" + "9" + "1000000000",
        )


if __name__ == '__main__':
    unittest.main()
