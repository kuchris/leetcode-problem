"""Tests for 76. Minimum Window Substring.

Oracle: enumerate every substring in order and keep the shortest one whose
Counter covers Counter(t). That shares no code with the sliding window under
test and only replaces the incumbent with a strictly shorter window, so it
breaks ties towards the earliest start exactly like the solution does.
"""

import itertools
import random
import unittest
from collections import Counter

from _loader import load_solution

Solution = load_solution('76-minimum-window-substring.py').Solution


def brute_force(s: str, t: str) -> str:
    """Shortest, then earliest, substring of s covering Counter(t)."""
    need = Counter(t)
    best = ''
    for start in range(len(s)):
        if best and len(best) == 1:
            break  # no window can be shorter than one character
        have: Counter = Counter()
        for end in range(start, len(s)):
            have[s[end]] += 1
            if all(have[ch] >= count for ch, count in need.items()):
                window = s[start:end + 1]
                if not best or len(window) < len(best):
                    best = window
                break  # any longer window from this start is worse
    return best


def is_valid_window(window: str, t: str) -> bool:
    have = Counter(window)
    return window and all(have[ch] >= count for ch, count in Counter(t).items())


class MinimumWindowSubstringTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().minWindow

    def test_official_examples(self):
        self.assertEqual(self.solve('ADOBECODEBANC', 'ABC'), 'BANC')
        self.assertEqual(self.solve('a', 'a'), 'a')
        self.assertEqual(self.solve('a', 'aa'), '')

    def test_no_window_exists(self):
        self.assertEqual(self.solve('a', 'b'), '')
        self.assertEqual(self.solve('abc', 'd'), '')
        self.assertEqual(self.solve('abc', 'abcd'), '')
        self.assertEqual(self.solve('aaab', 'baaaab'), '')

    def test_single_character(self):
        self.assertEqual(self.solve('z', 'z'), 'z')
        self.assertEqual(self.solve('za', 'a'), 'a')
        self.assertEqual(self.solve('az', 'z'), 'z')

    def test_repeated_characters_in_t(self):
        self.assertEqual(self.solve('aa', 'aa'), 'aa')
        self.assertEqual(self.solve('aaa', 'aa'), 'aa')
        self.assertEqual(self.solve('abab', 'aabb'), 'abab')
        self.assertEqual(self.solve('bbaa', 'aabb'), 'bbaa')

    def test_window_is_the_whole_string(self):
        self.assertEqual(self.solve('ba', 'ab'), 'ba')

    def test_shortest_window_is_not_the_first_valid_one(self):
        # The classic case: the first covering window ADOBEC is longer than BANC.
        self.assertEqual(self.solve('ADOBECODEBANC', 'ABC'), 'BANC')
        self.assertEqual(self.solve('cabwefgewcwaefgcf', 'cae'), 'cwae')

    def test_mixed_case_letters(self):
        # Case matters: 'AB' needs an uppercase B, so 'Ab' (A + lowercase b)
        # is not a valid window and the answer is the three-character 'AbB'.
        self.assertEqual(self.solve('aAbB', 'AB'), 'AbB')
        self.assertEqual(self.solve('xxYyX', 'YX'), 'YyX')
        self.assertEqual(self.solve('AABB', 'ab'), '')

    def test_exhaustive_small_cases(self):
        for s_length in range(1, 6):
            for s_chars in itertools.product('ab', repeat=s_length):
                s = ''.join(s_chars)
                for t_length in range(1, 4):
                    for t_chars in itertools.product('ab', repeat=t_length):
                        t = ''.join(t_chars)
                        with self.subTest(s=s, t=t):
                            self.assertEqual(self.solve(s, t), brute_force(s, t))

    def test_randomised_cases(self):
        rng = random.Random(760)
        alphabet = 'abc'
        for _ in range(300):
            s = ''.join(rng.choice(alphabet) for _ in range(rng.randint(1, 40)))
            t = ''.join(rng.choice(alphabet) for _ in range(rng.randint(1, 6)))
            with self.subTest(s=s, t=t):
                self.assertEqual(self.solve(s, t), brute_force(s, t))

    def test_randomised_single_letter_alphabet(self):
        rng = random.Random(761)
        for _ in range(100):
            s = 'a' * rng.randint(1, 30)
            t = 'a' * rng.randint(1, 32)
            with self.subTest(len_s=len(s), len_t=len(t)):
                self.assertEqual(self.solve(s, t), brute_force(s, t))

    def test_constraint_sized(self):
        rng = random.Random(762)
        alphabet = [ch for ch in 'abcdefghijklmnopqrstuvwxyz'
                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if ch not in 'QqZz']
        filler = ''.join(rng.choice(alphabet) for _ in range(100000 - 4))
        cut = 98765
        s = filler[:cut] + 'QqZz' + filler[cut:]
        self.assertEqual(len(s), 100000)

        # Q, q, Z and z appear exactly once each and consecutively, so the only
        # window covering t is the planted block itself.
        result = self.solve(s, 'QqZz')
        self.assertEqual(result, 'QqZz')
        self.assertTrue(is_valid_window(result, 'QqZz'))

        # t equal to the whole alphabet forces a window of length >= 52.
        t = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        result = self.solve(s, t)
        self.assertTrue(is_valid_window(result, t))
        self.assertGreaterEqual(len(result), 52)
        self.assertLessEqual(len(result), 100000)

    def test_constraint_sized_no_answer(self):
        s = 'a' * 100000
        self.assertEqual(self.solve(s, 'a' * 100000), 'a' * 100000)
        self.assertEqual(self.solve(s, 'b'), '')


if __name__ == '__main__':
    unittest.main()
