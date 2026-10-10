import itertools
import unittest

from _loader import load_solution

Solution = load_solution('17-letter-combinations-of-a-phone-number.py').Solution

LETTERS = {
    '2': 'abc', '3': 'def', '4': 'ghi', '5': 'jkl',
    '6': 'mno', '7': 'pqrs', '8': 'tuv', '9': 'wxyz',
}


def brute_force(digits: str) -> list[str]:
    """Independent oracle: the Cartesian product of the per-digit letters."""
    if not digits:
        return []
    return [''.join(p) for p in itertools.product(*(LETTERS[d] for d in digits))]


class LetterCombinationsTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().letterCombinations

    def test_official_examples(self):
        self.assertEqual(
            sorted(self.solve('23')),
            sorted(['ad', 'ae', 'af', 'bd', 'be', 'bf', 'cd', 'ce', 'cf']),
        )
        self.assertEqual(sorted(self.solve('2')), ['a', 'b', 'c'])

    def test_empty_input(self):
        self.assertEqual(self.solve(''), [])

    def test_four_digit_digit(self):
        self.assertEqual(sorted(self.solve('7')), ['p', 'q', 'r', 's'])

    def test_maximum_length(self):
        result = self.solve('9999')
        self.assertEqual(len(result), 4 ** 4)
        self.assertEqual(len(set(result)), 4 ** 4)

    def test_exhaustive_all_digit_strings(self):
        for size in range(1, 5):
            for digits in itertools.product('23456789', repeat=size):
                text = ''.join(digits)
                with self.subTest(digits=text):
                    self.assertEqual(
                        sorted(self.solve(text)), sorted(brute_force(text))
                    )


if __name__ == '__main__':
    unittest.main()
