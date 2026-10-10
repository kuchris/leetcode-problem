import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('44-wildcard-matching.py').Solution


def dp_oracle(s: str, p: str) -> bool:
    """Independent O(n*m) table: table[i][j] means s[:i] matches p[:j]."""
    n, m = len(s), len(p)
    table = [[False] * (m + 1) for _ in range(n + 1)]
    table[0][0] = True
    for j in range(1, m + 1):
        if p[j - 1] == '*':
            table[0][j] = table[0][j - 1]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if p[j - 1] == '*':
                # '*' matches empty (table[i][j-1]) or one more char (table[i-1][j]).
                table[i][j] = table[i][j - 1] or table[i - 1][j]
            elif p[j - 1] == '?' or p[j - 1] == s[i - 1]:
                table[i][j] = table[i - 1][j - 1]
    return table[n][m]


class WildcardMatchingTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().isMatch

    def test_official_examples(self):
        self.assertFalse(self.solve('aa', 'a'))
        self.assertTrue(self.solve('aa', '*'))
        self.assertFalse(self.solve('cb', '?a'))

    def test_empty_inputs(self):
        self.assertTrue(self.solve('', ''))
        self.assertTrue(self.solve('', '*'))
        self.assertTrue(self.solve('', '**'))
        self.assertFalse(self.solve('', '?'))
        self.assertFalse(self.solve('a', ''))

    def test_star_matches_empty_and_many(self):
        self.assertTrue(self.solve('ab', 'a*b'))
        self.assertTrue(self.solve('a' + 'b' * 10, 'a*b'))
        self.assertFalse(self.solve('ac', 'a*b'))

    def test_consecutive_stars_behave_as_one(self):
        self.assertTrue(self.solve('abc', 'a**c'))
        self.assertTrue(self.solve('abc', '***'))

    def test_question_mark_matches_exactly_one(self):
        self.assertTrue(self.solve('a', '?'))
        self.assertFalse(self.solve('', '?'))
        self.assertFalse(self.solve('ab', '?'))

    def test_maximum_length(self):
        s = 'a' * 2000
        self.assertTrue(self.solve(s, '*' + 'a' * 2000))
        self.assertTrue(self.solve(s, '?' * 2000))
        self.assertFalse(self.solve(s, '?' * 1999))
        self.assertTrue(self.solve(s, 'a*' * 1))

    def test_star_heavy_pattern_over_maximum_input(self):
        s = 'ab' * 1000
        self.assertTrue(self.solve(s, '*a*b*a*'))
        self.assertTrue(self.solve(s, 'a' + '*' * 100 + 'b'))

    def test_exhaustive_small_cases(self):
        strings = ['']
        for size in range(1, 5):
            strings += [''.join(c) for c in itertools.product('ab', repeat=size)]
        patterns = ['']
        for size in range(1, 4):
            patterns += [''.join(c) for c in itertools.product('ab?*', repeat=size)]
        for s in strings:
            for p in patterns:
                with self.subTest(s=s, p=p):
                    self.assertEqual(self.solve(s, p), dp_oracle(s, p))

    def test_randomised_cases(self):
        rng = random.Random(44)
        for _ in range(300):
            s = ''.join(rng.choice('ab') for _ in range(rng.randint(0, 12)))
            p = ''.join(rng.choice('ab?*') for _ in range(rng.randint(0, 8)))
            with self.subTest(s=s, p=p):
                self.assertEqual(self.solve(s, p), dp_oracle(s, p))


if __name__ == '__main__':
    unittest.main()
