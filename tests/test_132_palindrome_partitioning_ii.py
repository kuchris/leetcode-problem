"""Tests for 132. Palindrome Partitioning II.

Four ways to get the expected number of cuts, none of which expands around a
centre the way the solution does:

  - `mask_min_cuts` enumerates all 2^(n-1) cut masks and keeps the shortest one
    whose pieces are all palindromes -- brute force, used for every small case;
  - `bfs_cuts` is a BFS over cut positions: an edge i -> j exists when s[i:j] is a
    palindrome, and the answer is the fewest pieces minus one;
  - `palindrome_table_dp` fills the whole O(n^2) interval palindrome table and
    runs a DP over *suffixes* -- the opposite direction from the solution and
    with the opposite space complexity;
  - `bitset_dp` packs the palindromic ends of each start into Python integers and
    relaxes a prefix DP from those bitsets, which is what makes n = 2000
    checkable without an O(n^2) table.

`oracles_agree` cross-checks the fast oracle against the slow ones before they
are used on the constraint-sized inputs.
"""

import collections
import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('132-palindrome-partitioning-ii.py').Solution


def mask_min_cuts(s: str) -> int:
    """Fewest cuts, by enumerating every set of cut positions."""
    n = len(s)
    best = n - 1
    for mask in range(1 << (n - 1)):
        pieces = []
        start = 0
        for index in range(n - 1):
            if mask >> index & 1:
                pieces.append(s[start:index + 1])
                start = index + 1
        pieces.append(s[start:])
        if all(piece == piece[::-1] for piece in pieces):
            best = min(best, len(pieces) - 1)
    return best


def bfs_cuts(s: str) -> int:
    """Fewest pieces covering s, minus one, via BFS on cut positions."""
    n = len(s)
    pieces = [0] + [-1] * n
    queue = collections.deque([0])
    while queue:
        start = queue.popleft()
        for end in range(start + 1, n + 1):
            piece = s[start:end]
            if pieces[end] < 0 and piece == piece[::-1]:
                pieces[end] = pieces[start] + 1
                queue.append(end)
    return pieces[n] - 1


def palindrome_table_dp(s: str) -> int:
    """Interval palindrome table + DP over suffixes."""
    n = len(s)
    is_palindrome = [[False] * n for _ in range(n)]
    for start in range(n - 1, -1, -1):
        for end in range(start, n):
            is_palindrome[start][end] = s[start] == s[end] and (end - start < 2 or is_palindrome[start + 1][end - 1])

    best = [n + 1] * (n + 1)
    best[n] = 0
    for start in range(n - 1, -1, -1):
        for end in range(start, n):
            if is_palindrome[start][end] and best[end + 1] + 1 < best[start]:
                best[start] = best[end + 1] + 1
    return best[0] - 1


def bitset_dp(s: str) -> int:
    """Prefix DP whose palindromic ends come from per-start integer bitsets."""
    n = len(s)
    letter_mask = {}
    for index, char in enumerate(s):
        letter_mask[char] = letter_mask.get(char, 0) | (1 << index)

    palindromic = [0] * (n + 1)
    for start in range(n - 1, -1, -1):
        # Bit k of palindromic[start] means s[start:k + 1] is a palindrome. The
        # `1 << start` stands for the empty substring s[start + 1:start + 1].
        palindromic[start] = (1 << start) | (
            letter_mask[s[start]] & ((palindromic[start + 1] | (1 << start)) << 1)
        )

    cuts = list(range(-1, n))  # cuts[i] = i - 1, the all-singletons partition
    for start in range(n):
        base = cuts[start] + 1
        mask = palindromic[start] >> start
        while mask:
            low = mask & -mask
            end = start + low.bit_length() - 1
            if base < cuts[end + 1]:
                cuts[end + 1] = base
            mask ^= low
    return cuts[n]


class PalindromePartitioningTwoTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().minCut

    def test_official_examples(self):
        self.assertEqual(self.solve('aab'), 1)
        self.assertEqual(self.solve('a'), 0)
        self.assertEqual(self.solve('ab'), 1)

    def test_single_and_double_characters(self):
        for char in 'abcxyz':
            with self.subTest(char=char):
                self.assertEqual(self.solve(char), 0)
        self.assertEqual(self.solve('aa'), 0)
        self.assertEqual(self.solve('ab'), 1)
        self.assertEqual(self.solve('ba'), 1)

    def test_all_equal_characters(self):
        for length in range(1, 30):
            with self.subTest(length=length):
                self.assertEqual(self.solve('a' * length), 0)

    def test_alternating_families(self):
        # "abab..." of odd length is itself a palindrome; of even length the
        # first character splits off and the rest is an odd-length palindrome.
        for repeats in range(1, 12):
            with self.subTest(repeats=repeats):
                self.assertEqual(self.solve('ab' * repeats + 'a'), 0)
                self.assertEqual(self.solve('ab' * repeats), 1)
                self.assertEqual(self.solve('ba' * repeats), 1)
                self.assertEqual(self.solve('ba' * repeats + 'b'), 0)

    def test_distinct_characters_force_singletons(self):
        for length in range(1, 20):
            s = ''.join(chr(97 + index % 26) for index in range(length))
            with self.subTest(s=s):
                if len(set(s)) == len(s):
                    self.assertEqual(self.solve(s), length - 1)
                else:
                    self.assertEqual(self.solve(s), mask_min_cuts(s))

    def test_exhaustive_binary_strings(self):
        for length in range(1, 10):
            for chars in itertools.product('ab', repeat=length):
                s = ''.join(chars)
                with self.subTest(s=s):
                    expected = mask_min_cuts(s)
                    self.assertEqual(self.solve(s), expected)
                    self.assertEqual(expected, bfs_cuts(s))
                    self.assertEqual(expected, palindrome_table_dp(s))

    def test_exhaustive_ternary_strings(self):
        for length in range(1, 7):
            for chars in itertools.product('abc', repeat=length):
                s = ''.join(chars)
                with self.subTest(s=s):
                    expected = mask_min_cuts(s)
                    self.assertEqual(self.solve(s), expected)
                    self.assertEqual(expected, bfs_cuts(s))
                    self.assertEqual(expected, bitset_dp(s))

    def test_exhaustive_quaternary_strings(self):
        for length in range(1, 6):
            for chars in itertools.product('abcd', repeat=length):
                s = ''.join(chars)
                with self.subTest(s=s):
                    self.assertEqual(self.solve(s), mask_min_cuts(s))

    def test_randomised_small_strings(self):
        rng = random.Random(1320)
        for _ in range(300):
            length = rng.randint(1, 13)
            s = ''.join(rng.choice('abc') for _ in range(length))
            with self.subTest(s=s):
                expected = mask_min_cuts(s)
                self.assertEqual(self.solve(s), expected)
                self.assertEqual(expected, bfs_cuts(s))

    def test_randomised_medium_strings(self):
        rng = random.Random(1321)
        for _ in range(60):
            length = rng.randint(20, 150)
            alphabet = rng.choice(['ab', 'abc', 'abcdefghij'])
            s = ''.join(rng.choice(alphabet) for _ in range(length))
            with self.subTest(length=length, alphabet=alphabet):
                expected = palindrome_table_dp(s)
                self.assertEqual(self.solve(s), expected)
                self.assertEqual(expected, bitset_dp(s))

    def test_oracles_agree(self):
        # The bitset oracle is used on the constraint-sized inputs, so cross-check
        # it against the two slower oracles first.
        for length in range(1, 9):
            for chars in itertools.product('ab', repeat=length):
                s = ''.join(chars)
                with self.subTest(s=s):
                    self.assertEqual(bitset_dp(s), palindrome_table_dp(s))
                    self.assertEqual(bitset_dp(s), bfs_cuts(s))
        rng = random.Random(1322)
        for _ in range(40):
            s = ''.join(rng.choice('abc') for _ in range(rng.randint(30, 120)))
            with self.subTest(length=len(s)):
                self.assertEqual(bitset_dp(s), palindrome_table_dp(s))

    def test_constraint_sized_all_equal(self):
        # The worst case for the centre expansion: every centre runs to the end.
        s = 'a' * 2000
        self.assertEqual(self.solve(s), 0)
        self.assertEqual(self.solve(s), bitset_dp(s))

    def test_constraint_sized_alternating(self):
        s = 'ab' * 1000
        self.assertEqual(self.solve(s), 1)
        self.assertEqual(self.solve(s), bitset_dp(s))

    def test_constraint_sized_random_binary(self):
        rng = random.Random(1323)
        s = ''.join(rng.choice('ab') for _ in range(2000))
        expected = bitset_dp(s)
        self.assertEqual(self.solve(s), expected)
        self.assertLessEqual(expected, 1999)

    def test_constraint_sized_random_letters(self):
        rng = random.Random(1324)
        s = ''.join(rng.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(2000))
        self.assertEqual(self.solve(s), bitset_dp(s))

    def test_constraint_sized_three_letter_pattern(self):
        s = 'abc' * 666 + 'ab'
        self.assertEqual(len(s), 2000)
        self.assertEqual(self.solve(s), bitset_dp(s))

    def test_constraint_sized_distinct_characters(self):
        # 2000 characters that repeat only every 26 positions: no substring of
        # length 1 or 2 other than a doubled letter can be a palindrome.
        s = ''.join(chr(97 + index % 26) for index in range(2000))
        expected = bitset_dp(s)
        self.assertEqual(self.solve(s), expected)
        self.assertEqual(self.solve(s), 1999)

    def test_constraint_sized_half_palindrome(self):
        rng = random.Random(1325)
        half = ''.join(rng.choice('ab') for _ in range(1000))
        s = half + half[::-1]
        self.assertEqual(len(s), 2000)
        expected = bitset_dp(s)
        self.assertEqual(self.solve(s), expected)
        self.assertLessEqual(expected, 1)


if __name__ == '__main__':
    unittest.main()
