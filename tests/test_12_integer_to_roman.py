import re
import unittest

from _loader import load_solution

Solution = load_solution('12-integer-to-roman.py').Solution

SYMBOL_VALUES = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}

# The canonical spelling rules: at most three repeats of each power of ten, and
# only the six listed subtractive pairs.
CANONICAL = re.compile(
    r'^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$'
)


def roman_to_int(text: str) -> int:
    """Independent decoder: subtract a symbol when a larger one follows it."""
    total = 0
    for index, symbol in enumerate(text):
        value = SYMBOL_VALUES[symbol]
        if index + 1 < len(text) and value < SYMBOL_VALUES[text[index + 1]]:
            total -= value
        else:
            total += value
    return total


class IntegerToRomanTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().intToRoman

    def test_official_examples(self):
        self.assertEqual(self.solve(3749), 'MMMDCCXLIX')
        self.assertEqual(self.solve(58), 'LVIII')
        self.assertEqual(self.solve(1994), 'MCMXCIV')

    def test_boundaries(self):
        self.assertEqual(self.solve(1), 'I')
        self.assertEqual(self.solve(4), 'IV')
        self.assertEqual(self.solve(9), 'IX')
        self.assertEqual(self.solve(3999), 'MMMCMXCIX')

    def test_subtractive_forms(self):
        for number, expected in ((4, 'IV'), (9, 'IX'), (40, 'XL'), (90, 'XC'),
                                 (400, 'CD'), (900, 'CM')):
            with self.subTest(number=number):
                self.assertEqual(self.solve(number), expected)

    def test_never_repeats_a_symbol_four_times(self):
        for number in range(1, 4000):
            with self.subTest(number=number):
                self.assertNotIn('IIII', self.solve(number))

    def test_exhaustive_round_trip_and_canonical_form(self):
        for number in range(1, 4000):
            with self.subTest(number=number):
                text = self.solve(number)
                self.assertRegex(text, CANONICAL)
                self.assertEqual(roman_to_int(text), number)


if __name__ == '__main__':
    unittest.main()
