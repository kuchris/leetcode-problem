"""Tests for 115. Distinct Subsequences.

Oracles, both independent of the rolling DP:

  - ``combinations_oracle``: a subsequence of length |t| is a set of positions of
    s, so enumerate every such position set with itertools and count the ones
    that spell t. No DP, no recursion, no matching rule.
  - ``recursive_oracle``: branch on "skip s[i]" / "match s[i] with t[j]" with no
    memoisation, i.e. the definition as a plain search.
  - ``math.comb`` covers the special family s = "a"*k, t = "a"*j, whose answer is
    C(k, j) in closed form.

Exhaustive sweep over all strings of length <= 7 on {a, b} for s and all strings
of length <= 4 on {a, b} for t, plus the C(k, j) family for k <= 12.

The constraint-sized cases are chosen so their answers stay inside the signed
32-bit range the statement guarantees, and each has an independently derivable
value.
"""

import itertools
import math
import random
import unittest

from _loader import load_solution

Solution = load_solution('115-distinct-subsequences.py').Solution


def combinations_oracle(s: str, t: str) -> int:
    if len(t) > len(s):
        return 0
    total = 0
    for positions in itertools.combinations(range(len(s)), len(t)):
        if all(s[index] == t[offset] for offset, index in enumerate(positions)):
            total += 1
    return total


def recursive_oracle(s: str, t: str) -> int:
    m, n = len(s), len(t)

    def count(i: int, j: int) -> int:
        if j == n:
            return 1
        if i == m:
            return 0
        total = count(i + 1, j)
        if s[i] == t[j]:
            total += count(i + 1, j + 1)
        return total

    return count(0, 0)


def strings_of_length(length: int, alphabet: str = 'ab'):
    for combination in itertools.product(alphabet, repeat=length):
        yield ''.join(combination)


class DistinctSubsequencesTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().numDistinct

    def check(self, s, t):
        produced = self.solve(s, t)
        self.assertEqual(produced, combinations_oracle(s, t), f'oracle(s={s!r}, t={t!r})')
        self.assertEqual(produced, recursive_oracle(s, t), f'recursion(s={s!r}, t={t!r})')
        return produced

    def test_official_examples(self):
        self.assertEqual(self.solve('rabbbit', 'rabbit'), 3)
        self.assertEqual(self.solve('babgbag', 'bag'), 5)
        self.assertEqual(self.check('rabbbit', 'rabbit'), 3)
        self.assertEqual(self.check('babgbag', 'bag'), 5)

    def test_target_longer_than_source(self):
        self.assertEqual(self.check('a', 'aa'), 0)
        self.assertEqual(self.check('abc', 'abcd'), 0)
        self.assertEqual(self.solve('a' * 100, 'a' * 101), 0)

    def test_identical_strings(self):
        self.assertEqual(self.check('a', 'a'), 1)
        self.assertEqual(self.check('abc', 'abc'), 1)
        self.assertEqual(self.check('aaa', 'aaa'), 1)

    def test_single_characters(self):
        self.assertEqual(self.check('a', 'b'), 0)
        self.assertEqual(self.check('aab', 'b'), 1)
        self.assertEqual(self.check('baa', 'b'), 1)
        self.assertEqual(self.check('aaaa', 'a'), 4)

    def test_empty_target_is_the_empty_subsequence(self):
        # Outside the stated constraints (1 <= t.length) but harmless: the empty
        # target is matched once, by taking nothing.
        self.assertEqual(self.solve('abc', ''), 1)
        self.assertEqual(self.solve('', ''), 1)

    def test_repeated_characters(self):
        self.assertEqual(self.check('aaa', 'aa'), 3)
        self.assertEqual(self.check('aaaa', 'aa'), 6)
        self.assertEqual(self.check('aaaa', 'aaa'), 4)
        self.assertEqual(self.solve('a' * 20, 'a' * 5), math.comb(20, 5))

    def test_exhaustive_small_cases(self):
        sources = [s for length in range(1, 8) for s in strings_of_length(length)]
        targets = [t for length in range(1, 5) for t in strings_of_length(length)]
        for s in sources:
            for t in targets:
                with self.subTest(s=s, t=t):
                    self.check(s, t)

    def test_exhaustive_closed_form_family(self):
        for k in range(0, 13):
            s = 'a' * k
            for j in range(0, k + 1):
                with self.subTest(k=k, j=j):
                    self.assertEqual(self.solve(s, 'a' * j), math.comb(k, j))

    def test_random_cases(self):
        rng = random.Random(1150)
        for _ in range(400):
            s = ''.join(rng.choice('abc') for _ in range(rng.randint(1, 14)))
            t = ''.join(rng.choice('abc') for _ in range(rng.randint(1, 5)))
            with self.subTest(s=s, t=t):
                self.check(s, t)

    def test_random_subsequence_targets(self):
        # t taken from a real subsequence of s, so the answer is at least 1.
        rng = random.Random(1151)
        for _ in range(200):
            s = ''.join(rng.choice('ab') for _ in range(rng.randint(1, 16)))
            size = rng.randint(1, min(6, len(s)))
            positions = sorted(rng.sample(range(len(s)), size))
            t = ''.join(s[index] for index in positions)
            with self.subTest(s=s, t=t):
                self.assertGreaterEqual(self.solve(s, t), 1)
                self.check(s, t)

    def test_constraint_sized(self):
        # 1000 characters for both strings is the constraint maximum; every
        # expected value below is derived independently of the DP.
        self.assertEqual(self.solve('a' * 1000, 'a' * 3), math.comb(1000, 3))  # 166167000
        self.assertEqual(self.solve('a' * 1000, 'a' * 3), 166_167_000)
        self.assertEqual(self.solve('a' * 1000, 'a' * 2), 499_500)
        self.assertEqual(self.solve('a' * 1000, 'a' * 999), 1000)
        self.assertEqual(self.solve('a' * 1000, 'a' * 1000), 1)
        self.assertEqual(self.solve('a' * 1000, 'b'), 0)

        # t equal to s in length: a length-999 subsequence of a 1000-character
        # string omits exactly one index; omitting the final 'a' reproduces the
        # pattern, any other omission shifts a character out of place.
        self.assertEqual(self.solve('abc' * 333 + 'a', 'abc' * 333), 1)
        self.assertEqual(self.solve('ab' * 500, 'ab' * 500), 1)

        # a^500 b^500 against "ab": any 'a' before any 'b'.
        self.assertEqual(self.solve('a' * 500 + 'b' * 500, 'ab'), 250_000)
        # The same source against "ba" is impossible.
        self.assertEqual(self.solve('a' * 500 + 'b' * 500, 'ba'), 0)

    def test_constraint_sized_dp_terminates_quickly(self):
        # Worst-case shaped input for the O(len(s) * len(t)) loop.
        s = 'ab' * 500
        t = ('ab' * 500)
        self.assertEqual(self.solve(s, t), 1)
        self.assertEqual(self.solve('a' * 1000, 'a' * 1000), 1)
        self.assertEqual(self.solve('ab' * 500, 'b' * 500), 1)


if __name__ == '__main__':
    unittest.main()
