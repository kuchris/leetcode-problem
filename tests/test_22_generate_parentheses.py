import itertools
import unittest

from _loader import load_solution

Solution = load_solution('22-generate-parentheses.py').Solution


def brute_force(n: int) -> list[str]:
    """Enumerate every bracket string of length 2n and keep the valid ones."""
    valid = []
    for candidate in itertools.product('()', repeat=2 * n):
        balance, ok = 0, True
        for char in candidate:
            balance += 1 if char == '(' else -1
            if balance < 0:
                ok = False
                break
        if ok and balance == 0:
            valid.append(''.join(candidate))
    return sorted(valid)


def catalan(n: int) -> int:
    result = 1
    for i in range(n):
        result = result * 2 * (2 * i + 1) // (i + 2)
    return result


def is_valid(text: str) -> bool:
    balance = 0
    for char in text:
        balance += 1 if char == '(' else -1
        if balance < 0:
            return False
    return balance == 0


class GenerateParenthesesTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().generateParenthesis

    def test_official_examples(self):
        self.assertEqual(
            sorted(self.solve(3)),
            sorted(['((()))', '(()())', '(())()', '()(())', '()()()']),
        )
        self.assertEqual(self.solve(1), ['()'])

    def test_no_duplicates_and_correct_count(self):
        for n in range(1, 9):
            with self.subTest(n=n):
                result = self.solve(n)
                self.assertEqual(len(result), catalan(n))
                self.assertEqual(len(set(result)), len(result))
                self.assertTrue(all(is_valid(r) for r in result))
                self.assertTrue(all(len(r) == 2 * n for r in result))

    def test_exhaustive_against_brute_force(self):
        for n in range(1, 6):
            with self.subTest(n=n):
                self.assertEqual(sorted(self.solve(n)), brute_force(n))


if __name__ == '__main__':
    unittest.main()
