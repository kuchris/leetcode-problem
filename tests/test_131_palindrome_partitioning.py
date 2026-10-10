"""Tests for 131. Palindrome Partitioning.

Two independent oracles:

  - `mask_oracle` enumerates every one of the 2^(n-1) cut masks, builds the
    pieces for that mask and keeps the masks whose pieces are all palindromes --
    no recursion, no palindrome table;
  - `count_by_dp` counts the palindromic partitions with the classic prefix DP,
    and that count must equal the number of partitions the solution returns.

The statement does not fix an order, so every comparison is made on the sorted
list of tuples.
"""

import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('131-palindrome-partitioning.py').Solution


def mask_oracle(s: str) -> list:
    """Every palindromic partition, by enumerating cut masks."""
    n = len(s)
    results = []
    for mask in range(1 << (n - 1)):
        pieces = []
        start = 0
        for index in range(n - 1):
            if mask >> index & 1:
                pieces.append(s[start:index + 1])
                start = index + 1
        pieces.append(s[start:])
        if all(piece == piece[::-1] for piece in pieces):
            results.append(tuple(pieces))
    return sorted(results)


def count_by_dp(s: str) -> int:
    n = len(s)
    ways = [0] * (n + 1)
    ways[0] = 1
    for end in range(1, n + 1):
        for start in range(end):
            piece = s[start:end]
            if piece == piece[::-1]:
                ways[end] += ways[start]
    return ways[n]


def normalize(partitions) -> list:
    return sorted(tuple(piece for piece in partition) for partition in partitions)


class PalindromePartitioningTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().partition

    def assert_partitions(self, s: str) -> list:
        """Check the answer against both oracles and the structural rules."""
        result = self.solve(s)
        expected = mask_oracle(s)

        self.assertEqual(normalize(result), expected)
        self.assertEqual(len(result), count_by_dp(s))
        for partition in result:
            with self.subTest(s=s, partition=partition):
                self.assertEqual(''.join(partition), s)
                self.assertTrue(all(piece == piece[::-1] for piece in partition))
                self.assertTrue(all(piece for piece in partition))
        self.assertEqual(len({tuple(partition) for partition in result}), len(result))
        return result

    def test_official_examples(self):
        self.assertEqual(self.solve('aab'), [['a', 'a', 'b'], ['aa', 'b']])
        self.assertEqual(self.solve('a'), [['a']])

    def test_single_characters(self):
        for char in 'abcdefghijklmnopqrstuvwxyz':
            with self.subTest(char=char):
                self.assertEqual(self.solve(char), [[char]])

    def test_no_multi_character_palindromes(self):
        self.assertEqual(self.assert_partitions('abcd'), [['a', 'b', 'c', 'd']])
        self.assertEqual(self.assert_partitions('abcdef'), [list('abcdef')])

    def test_all_equal_characters(self):
        self.assertEqual(len(self.solve('aaa')), 4)
        self.assertEqual(len(self.solve('aaaa')), 8)
        self.assert_partitions('aaaaa')

    def test_two_character_blocks(self):
        self.assertEqual(normalize(self.solve('aabb')), [('a', 'a', 'b', 'b'), ('a', 'a', 'bb'), ('aa', 'b', 'b'), ('aa', 'bb')])
        self.assert_partitions('aabbaa')

    def test_exhaustive_binary_strings(self):
        for length in range(1, 9):
            for chars in itertools.product('ab', repeat=length):
                s = ''.join(chars)
                with self.subTest(s=s):
                    self.assert_partitions(s)

    def test_exhaustive_ternary_strings(self):
        for length in range(1, 7):
            for chars in itertools.product('abc', repeat=length):
                s = ''.join(chars)
                with self.subTest(s=s):
                    self.assert_partitions(s)

    def test_exhaustive_quaternary_strings(self):
        for length in range(1, 5):
            for chars in itertools.product('abcd', repeat=length):
                s = ''.join(chars)
                with self.subTest(s=s):
                    self.assert_partitions(s)

    def test_randomised_strings(self):
        rng = random.Random(1310)
        for _ in range(300):
            length = rng.randint(1, 12)
            s = ''.join(rng.choice('abc') for _ in range(length))
            with self.subTest(s=s):
                self.assert_partitions(s)

    def test_randomised_binary_strings(self):
        rng = random.Random(1311)
        for _ in range(200):
            length = rng.randint(1, 13)
            s = ''.join(rng.choice('ab') for _ in range(length))
            with self.subTest(s=s):
                self.assert_partitions(s)

    def test_constraint_sized_all_equal(self):
        # n = 16 is the constraint maximum; every one of the 2^15 cut masks is a
        # valid palindromic partition.
        s = 'a' * 16
        result = self.solve(s)
        self.assertEqual(len(result), 2 ** 15)
        self.assertEqual(len(result), count_by_dp(s))
        self.assertEqual(normalize(result), mask_oracle(s))
        self.assertTrue(all(''.join(partition) == s for partition in result))

    def test_constraint_sized_mixed(self):
        for s in ('ab' * 8, 'aabbaabb' * 2, 'abcdabcdabcdabcd', 'aaaaaaaaaaaaaaab'):
            with self.subTest(s=s):
                self.assert_partitions(s)

    def test_constraint_sized_random(self):
        rng = random.Random(1312)
        for _ in range(20):
            s = ''.join(rng.choice('abc') for _ in range(16))
            with self.subTest(s=s):
                self.assert_partitions(s)

    def test_constraint_sized_worst_case_count_is_bounded(self):
        # The all-equal string maximises the answer size, and the problem's own
        # bound on the number of partitions is what makes n = 16 tractable.
        sizes = {length: count_by_dp('a' * length) for length in range(1, 17)}
        self.assertEqual(sizes[16], 2 ** 15)
        self.assertEqual([sizes[length] for length in range(1, 6)], [1, 2, 4, 8, 16])


if __name__ == '__main__':
    unittest.main()
