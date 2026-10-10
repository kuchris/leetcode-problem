import itertools
import unittest

from _loader import load_solution

Solution = load_solution('65-valid-number.py').Solution

DIGITS = '0123456789'


def is_integer_part(text: str) -> bool:
    """Optional sign followed by one or more digits."""
    if text[:1] in '+-':
        text = text[1:]
    return bool(text) and all(char in DIGITS for char in text)


def is_decimal_part(text: str) -> bool:
    """Optional sign, then digits with at most one dot and at least one digit."""
    if text[:1] in '+-':
        text = text[1:]
    if '.' in text:
        if text.count('.') > 1:
            return False
        whole, _, fraction = text.partition('.')
        return all(char in DIGITS for char in whole) and all(char in DIGITS for char in fraction) and bool(whole or fraction)
    return bool(text) and all(char in DIGITS for char in text)


def oracle(s: str) -> bool:
    """Independent validator: split off the exponent, then check each part."""
    lowered = s.lower()
    if lowered.count('e') > 1:
        return False
    if 'e' in lowered:
        mantissa, exponent = lowered.split('e')
        if not is_integer_part(exponent):
            return False
    else:
        mantissa = lowered
    return is_decimal_part(mantissa)


class ValidNumberTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().isNumber

    def test_official_valid_examples(self):
        for s in ['2', '0089', '-0.1', '+3.14', '4.', '-.9', '2e10', '-90E3',
                  '3e+7', '+6e-1', '53.5e93', '-123.456e789']:
            with self.subTest(s=s):
                self.assertTrue(self.solve(s))

    def test_official_invalid_examples(self):
        for s in ['abc', '1a', '1e', 'e3', '99e2.5', '--6', '-+3', '95a54e53']:
            with self.subTest(s=s):
                self.assertFalse(self.solve(s))

    def test_statement_examples(self):
        self.assertTrue(self.solve('0'))
        self.assertFalse(self.solve('e'))
        self.assertFalse(self.solve('.'))

    def test_bare_dot_and_bare_sign(self):
        self.assertFalse(self.solve('.'))
        self.assertFalse(self.solve('+'))
        self.assertFalse(self.solve('-'))
        self.assertFalse(self.solve('+.'))

    def test_exponent_requires_an_integer(self):
        self.assertFalse(self.solve('1e'))
        self.assertFalse(self.solve('1e+'))
        self.assertFalse(self.solve('1e1.5'))
        self.assertTrue(self.solve('1e0'))
        self.assertTrue(self.solve('1E+9'))

    def test_dot_variants(self):
        self.assertTrue(self.solve('1.'))
        self.assertTrue(self.solve('.1'))
        self.assertTrue(self.solve('1.1'))
        self.assertFalse(self.solve('1.1.1'))
        self.assertFalse(self.solve('..1'))

    def test_maximum_length_input(self):
        self.assertTrue(self.solve('1' * 20))
        self.assertTrue(self.solve('-' + '1' * 18 + '.5'))
        self.assertFalse(self.solve('1' * 20 + 'e'))

    def test_exhaustive_against_oracle(self):
        alphabet = '01.e+-'
        for size in range(1, 5):
            for chars in itertools.product(alphabet, repeat=size):
                s = ''.join(chars)
                with self.subTest(s=s):
                    self.assertEqual(self.solve(s), oracle(s))

    def test_exhaustive_with_letters(self):
        alphabet = '1eE.a'
        for size in range(1, 4):
            for chars in itertools.product(alphabet, repeat=size):
                s = ''.join(chars)
                with self.subTest(s=s):
                    self.assertEqual(self.solve(s), oracle(s))


if __name__ == '__main__':
    unittest.main()
