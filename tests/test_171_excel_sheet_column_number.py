"""Tests for 171. Excel Sheet Column Number.

Oracles:
  - ``positional_oracle``: the definition transcribed literally as a weighted
    sum, digit(d) * 26^(len-1-i), which is not Horner's rule and shares no step
    with the solution.
  - the inverse problem (168): the two are exact inverses, so round trips in both
    directions pin the 'Z' -> 'AA' carry from each side. Every title of length
    <= 3 (all 18278 of them) is checked exactly, plus random titles of length
    4..7 and the constraint boundary "FXSHRXW".
"""

import random
import unittest

from _loader import load_solution

Solution = load_solution('171-excel-sheet-column-number.py').Solution
InverseSolution = load_solution('168-excel-sheet-column-title.py').Solution

MAX_NUMBER = 2 ** 31 - 1


def positional_oracle(title: str) -> int:
    length = len(title)
    total = 0
    for index, char in enumerate(title):
        total += (ord(char) - ord('A') + 1) * 26 ** (length - 1 - index)
    return total


def titles_of_length(length: int):
    """Every title of exactly `length` letters, in numeric order."""
    total = 26 ** (length - 1)
    for offset in range(total):
        index = offset
        digits = []
        for _ in range(length):
            digits.append(chr(ord('A') + index % 26))
            index //= 26
        yield ''.join(reversed(digits))


class ExcelSheetColumnNumberTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().titleToNumber
        self.inverse = InverseSolution().convertToTitle

    def check(self, title):
        produced = self.solve(title)
        self.assertEqual(produced, positional_oracle(title), f'title={title!r}')
        self.assertGreaterEqual(produced, 1)
        self.assertLessEqual(produced, MAX_NUMBER)
        return produced

    def test_official_examples(self):
        self.assertEqual(self.solve('A'), 1)
        self.assertEqual(self.solve('AB'), 28)
        self.assertEqual(self.solve('ZY'), 701)
        self.assertEqual(self.check('A'), 1)
        self.assertEqual(self.check('AB'), 28)
        self.assertEqual(self.check('ZY'), 701)

    def test_single_letters(self):
        for index in range(26):
            char = chr(ord('A') + index)
            with self.subTest(char=char):
                self.assertEqual(self.check(char), index + 1)

    def test_carry_boundaries(self):
        expected = {
            'A': 1, 'Z': 26, 'AA': 27, 'AZ': 52, 'BA': 53, 'BZ': 78, 'CA': 79,
            'ZZ': 702, 'AAA': 703, 'AAZ': 728, 'ABA': 729,
            'ZZZ': 18278, 'AAAA': 18279,
        }
        for title, value in expected.items():
            with self.subTest(title=title):
                self.assertEqual(self.check(title), value)
                self.assertEqual(self.inverse(value), title)

    def test_constraint_sized(self):
        # 2^31 - 1 is the constraint maximum and "FXSHRXW" its title, so the whole
        # valid range is ["A", "FXSHRXW"].
        self.assertEqual(self.check('FXSHRXW'), MAX_NUMBER)
        self.assertEqual(self.solve('FXSHRXW'), 2147483647)
        self.assertEqual(self.inverse(MAX_NUMBER), 'FXSHRXW')
        titles = [self.inverse(value) for value in
                  (MAX_NUMBER, MAX_NUMBER - 1, MAX_NUMBER - 25, MAX_NUMBER - 26,
                   26 ** 6, 26 ** 6 + 1, 26 ** 6 - 1)]
        titles += ['AAAAAAA', 'ZZZ', 'ZZ']
        for title in titles:
            with self.subTest(title=title):
                self.assertEqual(self.solve(title), positional_oracle(title))

    def test_exhaustive_titles_up_to_three_letters(self):
        for length in (1, 2, 3):
            for title in titles_of_length(length):
                with self.subTest(length=length, title=title):
                    self.assertEqual(self.solve(title), positional_oracle(title))

    def test_random_titles(self):
        rng = random.Random(1710)
        for _ in range(2000):
            length = rng.randint(1, 7)
            title = ''.join(chr(ord('A') + rng.randrange(26)) for _ in range(length))
            if positional_oracle(title) > MAX_NUMBER:
                continue
            with self.subTest(title=title):
                self.check(title)

    def test_round_trip_forward(self):
        # columnNumber(columnTitle(n)) == n, on both sides of the carry.
        titles = [self.inverse(n) for n in range(1, 20_001)]
        rng = random.Random(1711)
        titles += [self.inverse(rng.randint(1, MAX_NUMBER)) for _ in range(1000)]
        titles += ['A', 'Z', 'AA', 'ZZ', 'FXSHRXW']
        for title in titles:
            with self.subTest(title=title):
                self.assertEqual(self.solve(title), positional_oracle(title))

    def test_round_trip_backward(self):
        # columnTitle(columnNumber(t)) == t
        rng = random.Random(1712)
        values = list(range(1, 20_001))
        values += [rng.randint(1, MAX_NUMBER) for _ in range(1000)]
        values += [MAX_NUMBER, MAX_NUMBER - 1, 26, 27, 702, 703]
        for n in values:
            with self.subTest(n=n):
                title = self.inverse(n)
                self.assertEqual(self.solve(title), n)
                self.assertEqual(self.inverse(self.solve(title)), title)


if __name__ == '__main__':
    unittest.main()
