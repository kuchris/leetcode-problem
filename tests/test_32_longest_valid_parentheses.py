import itertools
import unittest

from _loader import load_solution

Solution = load_solution('32-longest-valid-parentheses.py').Solution


def is_valid(text: str) -> bool:
    balance = 0
    for char in text:
        balance += 1 if char == '(' else -1
        if balance < 0:
            return False
    return balance == 0


def brute_force(s: str) -> int:
    """Longest valid substring, by checking every substring."""
    best = 0
    for i in range(len(s)):
        for j in range(i + 2, len(s) + 1, 2):
            if j - i > best and is_valid(s[i:j]):
                best = j - i
    return best


class LongestValidParenthesesTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().longestValidParentheses

    def test_official_examples(self):
        self.assertEqual(self.solve('(()'), 2)
        self.assertEqual(self.solve(')()())'), 4)
        self.assertEqual(self.solve(''), 0)

    def test_no_valid_pair(self):
        self.assertEqual(self.solve(')'), 0)
        self.assertEqual(self.solve('('), 0)
        self.assertEqual(self.solve(')('), 0)

    def test_whole_string_is_valid(self):
        self.assertEqual(self.solve('()'), 2)
        self.assertEqual(self.solve('()()'), 4)
        self.assertEqual(self.solve('(())'), 4)
        self.assertEqual(self.solve('(()())'), 6)

    def test_nested_and_concatenated_runs(self):
        self.assertEqual(self.solve('()(()'), 2)
        self.assertEqual(self.solve('(()())()'), 8)
        self.assertEqual(self.solve('())(()'), 2)

    def test_maximum_size(self):
        self.assertEqual(self.solve('()' * 15000), 30000)
        self.assertEqual(self.solve('(' * 15000 + ')' * 15000), 30000)
        self.assertEqual(self.solve(')' * 30000), 0)

    def test_exhaustive_small_cases(self):
        for size in range(0, 11):
            for candidate in itertools.product('()', repeat=size):
                s = ''.join(candidate)
                with self.subTest(s=s):
                    self.assertEqual(self.solve(s), brute_force(s))


if __name__ == '__main__':
    unittest.main()
