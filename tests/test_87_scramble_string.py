"""Tests for 87. Scramble String.

Two independent oracles:

  - `all_scrambles` applies the definition literally: it builds the closure of
    the left/right swap operation over every substring and the test then asks for
    membership. Generate-and-test, no early exit, no pruning.
  - `interval_dp` is a bottom-up interval DP over every (i, j, length) triple,
    computed from length 1 upwards. It uses the same characterisation but the
    opposite evaluation order (no recursion, no memo dict).

Scrambling itself is a one-way construction: many strings are claimed only when
they can be *built*, so nothing here relies on the solution's search order.
"""

import itertools
import random
import unittest
from functools import lru_cache

from _loader import load_solution

Solution = load_solution('87-scramble-string.py').Solution


@lru_cache(maxsize=None)
def all_scrambles(s: str) -> frozenset:
    """Every string reachable from s by the scramble operation."""
    if len(s) <= 1:
        return frozenset([s])
    out = set()
    for cut in range(1, len(s)):
        for left in all_scrambles(s[:cut]):
            for right in all_scrambles(s[cut:]):
                out.add(left + right)
                out.add(right + left)
    return frozenset(out)


def interval_dp(s1: str, s2: str) -> bool:
    """Bottom-up interval DP over all (start1, start2, length) triples."""
    n = len(s1)
    table = [[[False] * (n + 1) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            table[i][j][1] = s1[i] == s2[j]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            for j in range(n - length + 1):
                found = False
                for cut in range(1, length):
                    if table[i][j][cut] and table[i + cut][j + cut][length - cut]:
                        found = True
                        break
                    if table[i][j + length - cut][cut] and table[i + cut][j][length - cut]:
                        found = True
                        break
                table[i][j][length] = found
    return table[0][0][n]


def make_scramble(s: str, rng: random.Random) -> str:
    """Build a known scramble of s by replaying the recursive definition."""
    if len(s) <= 1:
        return s
    cut = rng.randint(1, len(s) - 1)
    left = make_scramble(s[:cut], rng)
    right = make_scramble(s[cut:], rng)
    return right + left if rng.random() < 0.5 else left + right


class ScrambleStringTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().isScramble

    def test_official_examples(self):
        self.assertTrue(self.solve('great', 'rgeat'))
        self.assertFalse(self.solve('abcde', 'caebd'))
        self.assertTrue(self.solve('a', 'a'))

    def test_length_one(self):
        self.assertTrue(self.solve('a', 'a'))
        self.assertFalse(self.solve('a', 'b'))
        self.assertTrue(self.solve('z', 'z'))

    def test_length_two(self):
        self.assertTrue(self.solve('ab', 'ab'))
        self.assertTrue(self.solve('ab', 'ba'))
        self.assertFalse(self.solve('ab', 'aa'))
        self.assertFalse(self.solve('aa', 'ab'))

    def test_identical_strings(self):
        for s in ('aa', 'abc', 'aabb', 'abcdefghij'):
            with self.subTest(s=s):
                self.assertTrue(self.solve(s, s))

    def test_different_character_multisets(self):
        self.assertFalse(self.solve('ab', 'aa'))
        self.assertFalse(self.solve('aab', 'abb'))
        self.assertFalse(self.solve('abcdef', 'abcdeg'))

    def test_the_same_letters_in_a_different_order_are_not_always_scrambles(self):
        # 'abcd' can move whole halves around, but c-a-d-b is unreachable.
        self.assertFalse(self.solve('abcd', 'cadb'))
        self.assertTrue(self.solve('abcd', 'badc'))

    def test_exhaustive_small_cases_two_letters(self):
        for length in range(1, 8):
            for s1 in itertools.product('ab', repeat=length):
                s1 = ''.join(s1)
                reachable = all_scrambles(s1)
                for s2 in itertools.product('ab', repeat=length):
                    s2 = ''.join(s2)
                    with self.subTest(s1=s1, s2=s2):
                        self.assertEqual(self.solve(s1, s2), s2 in reachable)

    def test_exhaustive_small_cases_three_letters(self):
        for length in range(1, 6):
            for s1 in itertools.product('abc', repeat=length):
                s1 = ''.join(s1)
                reachable = all_scrambles(s1)
                for s2 in itertools.product('abc', repeat=length):
                    s2 = ''.join(s2)
                    with self.subTest(s1=s1, s2=s2):
                        self.assertEqual(self.solve(s1, s2), s2 in reachable)

    def test_randomised_mid_sized_cases(self):
        rng = random.Random(870)
        for _ in range(150):
            length = rng.randint(6, 12)
            s1 = ''.join(rng.choice('abc') for _ in range(length))
            letters = list(s1)
            rng.shuffle(letters)
            s2 = ''.join(letters)
            with self.subTest(s1=s1, s2=s2):
                self.assertEqual(self.solve(s1, s2), interval_dp(s1, s2))

    def test_randomised_mid_sized_scrambles_are_accepted(self):
        rng = random.Random(871)
        for _ in range(100):
            length = rng.randint(6, 12)
            s1 = ''.join(rng.choice('abcd') for _ in range(length))
            s2 = make_scramble(s1, rng)
            with self.subTest(s1=s1, s2=s2):
                self.assertTrue(self.solve(s1, s2))
                self.assertEqual(sorted(s1), sorted(s2))

    def test_constraint_sized(self):
        # 30 characters is the constraint maximum.
        rng = random.Random(872)
        s1 = ''.join(rng.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(30))
        self.assertTrue(self.solve(s1, s1))

        s2 = make_scramble(s1, rng)
        self.assertTrue(self.solve(s1, s2))
        self.assertEqual(sorted(s1), sorted(s2))

        # Same length, different multiset: the count check rejects it outright.
        s3 = s1[:-1] + ('a' if s1[-1] != 'a' else 'b')
        self.assertFalse(self.solve(s1, s3))

        # Long runs of one letter are all mutually reachable.
        self.assertTrue(self.solve('a' * 30, 'a' * 30))
        self.assertFalse(self.solve('a' * 30, 'a' * 29 + 'b'))
        # The two halves can swap, so the reversed half-pair is reachable.
        self.assertTrue(self.solve('abcdefghijklmno' + 'pqrstuvwxyzabcd',
                                   'pqrstuvwxyzabcd' + 'abcdefghijklmno'))

    def test_constraint_sized_random_anagrams_match_the_dp(self):
        # Anagrams of a 30-character string, checked against the interval DP.
        rng = random.Random(873)
        for _ in range(10):
            s1 = ''.join(rng.choice('ab') for _ in range(30))
            letters = list(s1)
            rng.shuffle(letters)
            s2 = ''.join(letters)
            with self.subTest(s1=s1, s2=s2):
                self.assertEqual(self.solve(s1, s2), interval_dp(s1, s2))


if __name__ == '__main__':
    unittest.main()
