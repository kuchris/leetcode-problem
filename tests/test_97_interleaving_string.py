"""Tests for 97. Interleaving String.

Two oracles, both deliberately unlike the DP:

  - ``dfs_oracle``: enumerate every interleaving by recursing on the two source
    strings, with no memoisation and no DP table. It is exponential but it walks
    the definition directly.
  - ``subset_oracle``: an interleaving is exactly a choice of ``len(s1)``
    positions of s3 that spell s1 while the remaining positions spell s2, so
    ``itertools.combinations`` over the positions decides the question with no
    recursion at all.

The exhaustive sweep compares the solution against both, and the two oracles
against each other.
"""

import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('97-interleaving-string.py').Solution


def dfs_oracle(s1: str, s2: str, s3: str) -> bool:
    if len(s1) + len(s2) != len(s3):
        return False
    n1, n2 = len(s1), len(s2)

    def walk(i: int, j: int) -> bool:
        if i == n1 and j == n2:
            return True
        k = i + j
        if i < n1 and s1[i] == s3[k] and walk(i + 1, j):
            return True
        if j < n2 and s2[j] == s3[k] and walk(i, j + 1):
            return True
        return False

    return walk(0, 0)


def subset_oracle(s1: str, s2: str, s3: str) -> bool:
    if len(s1) + len(s2) != len(s3):
        return False
    for positions in itertools.combinations(range(len(s3)), len(s1)):
        taken = set(positions)
        if ''.join(s3[index] for index in positions) != s1:
            continue
        if ''.join(c for index, c in enumerate(s3) if index not in taken) != s2:
            continue
        return True
    return False


def strings_up_to(length: int, alphabet: str = 'ab'):
    for size in range(length + 1):
        for combination in itertools.product(alphabet, repeat=size):
            yield ''.join(combination)


def random_interleaving(s1: str, s2: str, rng: random.Random) -> str:
    """Merge s1 and s2 by repeatedly taking the next character of one of them."""
    out = []
    i = j = 0
    while i < len(s1) or j < len(s2):
        take_first = j >= len(s2) or (i < len(s1) and rng.random() < 0.5)
        if take_first:
            out.append(s1[i])
            i += 1
        else:
            out.append(s2[j])
            j += 1
    return ''.join(out)


class InterleavingStringTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().isInterleave

    def check(self, s1, s2, s3):
        return self.solve(s1, s2, s3)

    def test_official_examples(self):
        self.assertTrue(self.check('aabcc', 'dbbca', 'aadbbcbcac'))
        self.assertFalse(self.check('aabcc', 'dbbca', 'aadbbbaccc'))
        self.assertTrue(self.check('', '', ''))

    def test_length_mismatch_is_rejected(self):
        self.assertFalse(self.check('a', '', ''))
        self.assertFalse(self.check('', '', 'a'))
        self.assertFalse(self.check('ab', 'cd', 'abc'))
        self.assertFalse(self.check('ab', 'cd', 'abcde'))

    def test_one_source_empty(self):
        self.assertTrue(self.check('abc', '', 'abc'))
        self.assertTrue(self.check('', 'abc', 'abc'))
        self.assertFalse(self.check('abc', '', 'acb'))
        self.assertFalse(self.check('', 'abc', 'ab'))

    def test_first_or_second_string_first(self):
        # Both interleaving orders are accepted.
        self.assertTrue(self.check('ab', 'cd', 'abcd'))
        self.assertTrue(self.check('ab', 'cd', 'cdab'))
        self.assertTrue(self.check('ab', 'cd', 'acbd'))
        self.assertTrue(self.check('ab', 'cd', 'cadb'))
        self.assertFalse(self.check('ab', 'cd', 'abdc'))

    def test_repeated_characters(self):
        self.assertTrue(self.check('a', 'a', 'aa'))
        self.assertFalse(self.check('a', 'a', 'a'))
        self.assertFalse(self.check('aa', 'aa', 'aaa'))
        self.assertTrue(self.check('aaaa', 'aa', 'aaaaaa'))

    def test_exhaustive_small_cases(self):
        small = list(strings_up_to(3))
        for s1 in small:
            for s2 in small:
                for s3 in strings_up_to(len(s1) + len(s2)):
                    with self.subTest(s1=s1, s2=s2, s3=s3):
                        expected = dfs_oracle(s1, s2, s3)
                        self.assertEqual(subset_oracle(s1, s2, s3), expected)
                        self.assertEqual(self.check(s1, s2, s3), expected)

    def test_random_cases_with_constructed_interleavings(self):
        rng = random.Random(970)
        for _ in range(400):
            s1 = ''.join(rng.choice('abc') for _ in range(rng.randint(0, 8)))
            s2 = ''.join(rng.choice('abc') for _ in range(rng.randint(0, 8)))
            s3 = random_interleaving(s1, s2, rng)
            with self.subTest(s1=s1, s2=s2, s3=s3):
                self.assertTrue(self.check(s1, s2, s3))  # true by construction
                self.assertEqual(self.check(s1, s2, s3), dfs_oracle(s1, s2, s3))

    def test_random_near_misses(self):
        rng = random.Random(971)
        for _ in range(400):
            s1 = ''.join(rng.choice('ab') for _ in range(rng.randint(0, 6)))
            s2 = ''.join(rng.choice('ab') for _ in range(rng.randint(0, 6)))
            s3 = list(random_interleaving(s1, s2, rng))
            if not s3:
                continue
            index = rng.randrange(len(s3))
            s3[index] = rng.choice('ab')
            s3 = ''.join(s3)
            with self.subTest(s1=s1, s2=s2, s3=s3):
                self.assertEqual(self.check(s1, s2, s3), dfs_oracle(s1, s2, s3))
                self.assertEqual(self.check(s1, s2, s3), subset_oracle(s1, s2, s3))

    def test_random_unrelated_third_strings(self):
        rng = random.Random(972)
        for _ in range(200):
            s1 = ''.join(rng.choice('ab') for _ in range(rng.randint(0, 5)))
            s2 = ''.join(rng.choice('ab') for _ in range(rng.randint(0, 5)))
            s3 = ''.join(rng.choice('ab') for _ in range(len(s1) + len(s2)))
            with self.subTest(s1=s1, s2=s2, s3=s3):
                self.assertEqual(self.check(s1, s2, s3), dfs_oracle(s1, s2, s3))

    def test_constraint_sized(self):
        rng = random.Random(973)

        # 100 + 100 characters is the constraint maximum.
        s1 = ''.join(rng.choice('ab') for _ in range(100))
        s2 = ''.join(rng.choice('ab') for _ in range(100))

        # A real interleaving: true by construction.
        s3 = random_interleaving(s1, s2, rng)
        self.assertTrue(self.check(s1, s2, s3))

        # Concatenation is an interleaving too.
        self.assertTrue(self.check(s1, s2, s1 + s2))
        self.assertTrue(self.check(s1, s2, s2 + s1))

        # Same length, one letter replaced: the multiset no longer matches, and
        # an interleaving must be a permutation of s1 + s2, so it is false.
        flipped = ('b' if s3[0] == 'a' else 'a') + s3[1:]
        self.assertFalse(self.check(s1, s2, flipped))

        # All identical letters, maximum size.
        ones = 'a' * 100
        self.assertTrue(self.check(ones, ones, 'a' * 200))
        self.assertFalse(self.check(ones, ones, 'a' * 199))

        # A block case that is false although the multisets agree:
        # s1 = a^50 b^50, s2 = b^50 a^50, s3 = a^100 b^100. The 100 a's of s3
        # come first, but s2's a's sit behind its 50 b's, so consuming them
        # would place b's inside the all-a prefix.
        blocks = 'a' * 50 + 'b' * 50
        reordered = 'b' * 50 + 'a' * 50
        self.assertFalse(self.check(blocks, reordered, 'a' * 100 + 'b' * 100))
        # The same two sources do interleave into blocks + reordered.
        self.assertTrue(self.check(blocks, reordered, blocks + reordered))
        self.assertTrue(self.check(blocks, reordered, reordered + blocks))


if __name__ == '__main__':
    unittest.main()
