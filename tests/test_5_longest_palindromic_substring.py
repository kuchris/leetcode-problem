import itertools
import unittest

from _loader import load_solution

Solution = load_solution('5-longest-palindromic-substring.py').Solution


def brute_force(s: str) -> int:
    """Longest palindromic substring length, by checking every substring."""
    best = 0
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            candidate = s[i:j]
            if candidate == candidate[::-1]:
                best = max(best, len(candidate))
    return best


class LongestPalindromicSubstringTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().longestPalindrome

    def assert_valid(self, s: str, result: str, expected_length: int):
        self.assertIn(result, s, f'{result!r} is not a substring of {s!r}')
        self.assertEqual(result, result[::-1], f'{result!r} is not a palindrome')
        self.assertEqual(len(result), expected_length, f'wrong length for {s!r}')

    def test_official_examples(self):
        # Both "bab" and "aba" are accepted, so check the length, not the text.
        self.assert_valid('babad', self.solve('babad'), 3)
        self.assert_valid('cbbd', self.solve('cbbd'), 2)

    def test_single_character_and_uniform_string(self):
        self.assertEqual(self.solve('a'), 'a')
        self.assertEqual(self.solve('aaaa'), 'aaaa')
        self.assertEqual(self.solve('ab'), 'a')

    def test_no_palindrome_longer_than_one(self):
        self.assert_valid('abcd', self.solve('abcd'), 1)

    def test_maximum_length_input(self):
        # An alternating string is palindromic at every odd length, so the
        # longest palindrome is the largest odd length that fits.
        s = 'ab' * 500
        self.assert_valid(s, self.solve(s), 999)
        s = 'a' * 1000
        self.assertEqual(self.solve(s), s)

    def test_all_distinct_characters(self):
        s = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        self.assert_valid(s, self.solve(s), 1)

    def test_exhaustive_small_strings(self):
        for size in range(1, 8):
            for letters in itertools.product('ab', repeat=size):
                s = ''.join(letters)
                with self.subTest(s=s):
                    self.assert_valid(s, self.solve(s), brute_force(s))


if __name__ == '__main__':
    unittest.main()
