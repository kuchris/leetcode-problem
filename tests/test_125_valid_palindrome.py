"""Tests for 125. Valid Palindrome.

Two independent oracles, neither of which uses two moving pointers:

  - `filtered_reverse` builds the alphanumeric lowercase string with a
    comprehension and compares it with its own reverse -- the definition from
    the statement, done with whole-string operations.
  - `regex_reverse` deletes everything outside ``[0-9a-z]`` with `re` and
    compares with the reverse; it shares no code with either of the others.

The statement guarantees printable ASCII, which is the only reason an
ASCII-only regex is a valid oracle for `str.isalnum`.
"""

import itertools
import random
import re
import string
import unittest

from _loader import load_solution

Solution = load_solution('125-valid-palindrome.py').Solution

PRINTABLE = string.ascii_letters + string.digits + string.punctuation + ' '


def filtered_reverse(s: str) -> bool:
    kept = [c.lower() for c in s if c.isalnum()]
    return kept == kept[::-1]


def regex_reverse(s: str) -> bool:
    kept = re.sub(r'[^0-9a-z]', '', s.lower())
    return kept == kept[::-1]


class ValidPalindromeTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().isPalindrome

    def test_official_examples(self):
        self.assertTrue(self.solve('A man, a plan, a canal: Panama'))
        self.assertFalse(self.solve('race a car'))
        self.assertTrue(self.solve(' '))

    def test_single_characters(self):
        for c in 'aZ0 !?,.':
            with self.subTest(c=c):
                self.assertTrue(self.solve(c))

    def test_only_punctuation(self):
        for s in ('.', ',.', '...', '., ,.', '\t\n'):
            with self.subTest(s=s):
                self.assertTrue(self.solve(s))

    def test_case_and_digit_handling(self):
        self.assertTrue(self.solve('Aa'))
        self.assertFalse(self.solve('aA b'))
        self.assertFalse(self.solve('0P'))
        self.assertTrue(self.solve('0P0'))
        self.assertTrue(self.solve('ab2ba'))
        self.assertFalse(self.solve('ab2bc'))
        self.assertTrue(self.solve('1a2b2a1'))
        self.assertFalse(self.solve('1a2b2a2'))

    def test_punctuation_between_mirrors(self):
        self.assertTrue(self.solve('a.b,a'))
        self.assertFalse(self.solve('a.b,c'))
        self.assertTrue(self.solve('!!!a,b,a!!!'))
        self.assertFalse(self.solve('!!!a,b,c!!!'))

    def test_two_pointer_skip_edge_cases(self):
        # A run of punctuation on one side only must not shift the pointers.
        self.assertTrue(self.solve('ab,,,ba'))
        self.assertTrue(self.solve(',,,abba,,,'))
        self.assertFalse(self.solve('ab,,,bc'))
        self.assertTrue(self.solve('a' + ',' * 50 + 'a'))
        self.assertFalse(self.solve('a' + ',' * 50 + 'b'))

    def test_exhaustive_short_strings(self):
        alphabet = 'aA1, '
        for length in range(1, 5):
            for chars in itertools.product(alphabet, repeat=length):
                s = ''.join(chars)
                with self.subTest(s=s):
                    expected = filtered_reverse(s)
                    self.assertEqual(self.solve(s), expected)
                    self.assertEqual(expected, regex_reverse(s))

    def test_exhaustive_palindrome_shaped_strings(self):
        # Every string built by mirroring a half, with punctuation injected.
        rng = random.Random(1250)
        for length in range(1, 6):
            for half in itertools.product('aB1,', repeat=length):
                left = ''.join(half)
                mirrored = left + ''.join(rng.choice('!, .') for _ in range(rng.randint(0, 2))) + left[::-1]
                with self.subTest(s=mirrored):
                    self.assertTrue(self.solve(mirrored))

    def test_randomised_printable_ascii(self):
        rng = random.Random(125)
        for _ in range(500):
            s = ''.join(rng.choice(PRINTABLE) for _ in range(rng.randint(1, 24)))
            with self.subTest(s=s):
                self.assertEqual(self.solve(s), filtered_reverse(s))

    def test_randomised_mirrored_strings(self):
        rng = random.Random(1251)
        for _ in range(300):
            half = ''.join(rng.choice(PRINTABLE) for _ in range(rng.randint(1, 20)))
            self.assertTrue(self.solve(half + ''.join(reversed(half))))

    def test_constraint_sized(self):
        # 2 * 10^5 printable ASCII characters is the constraint maximum.
        half = 'A1' * 50000  # 100000 characters
        self.assertEqual(len(half), 100000)

        palindrome = half + '!' + ''.join(reversed(half))
        self.assertEqual(len(palindrome), 200001)
        self.assertTrue(self.solve(palindrome))
        self.assertTrue(regex_reverse(palindrome))

        even = half + ''.join(reversed(half))
        self.assertEqual(len(even), 200000)
        self.assertTrue(self.solve(even))

        broken = half + '!' + ''.join(reversed(half))[:-1] + 'b'
        self.assertEqual(len(broken), 200001)
        self.assertFalse(self.solve(broken))
        self.assertEqual(self.solve(broken), filtered_reverse(broken))

        punctuation = ',' * 200000
        self.assertTrue(self.solve(punctuation))

    def test_constraint_sized_random(self):
        rng = random.Random(1252)
        for _ in range(20):
            s = ''.join(rng.choice(PRINTABLE) for _ in range(200000))
            with self.subTest(seed=len(s)):
                self.assertEqual(self.solve(s), filtered_reverse(s))


if __name__ == '__main__':
    unittest.main()
