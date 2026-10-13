"""Tests for 168. Excel Sheet Column Title.

Oracles:
  - ``length_first_oracle``: a different construction of the same numbering.
    Titles of length 1..L number 26 + 26^2 + ... + 26^L, so the length is found
    first, and the title is then the ordinary base-26 representation of the
    0-based offset inside that block, zero-padded to the length. It shares no
    step with the solution's repeated divmod(n - 1, 26).
  - the inverse problem (171): the two are exact inverses, so a round trip in
    both directions is a stronger check than either direction alone -- it pins
    the 'Z' -> 'AA' carry from both sides. The forward direction is verified for
    every n in 1..20000 plus random values up to the 2^31 - 1 constraint, and the
    backward direction for every title of length <= 3 (all 18278 of them, the
    whole ZZZ block) plus random longer titles.
"""

import random
import re
import unittest

from _loader import load_solution

Solution = load_solution('168-excel-sheet-column-title.py').Solution
InverseSolution = load_solution('171-excel-sheet-column-number.py').Solution

TITLE = re.compile(r'^[A-Z]{1,7}$')
MAX_NUMBER = 2 ** 31 - 1


def count_up_to(length: int) -> int:
    """How many titles have at most `length` letters."""
    return 26 * (26 ** length - 1) // 25


def length_first_oracle(n: int) -> str:
    length = 1
    while count_up_to(length) < n:
        length += 1
    index = n - count_up_to(length - 1) - 1   # 0-based offset in this block
    digits = []
    for _ in range(length):
        digits.append(chr(ord('A') + index % 26))
        index //= 26
    return ''.join(reversed(digits))


class ExcelSheetColumnTitleTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().convertToTitle
        self.inverse = InverseSolution().titleToNumber

    def check(self, n):
        produced = self.solve(n)
        self.assertEqual(produced, length_first_oracle(n), f'n={n}')
        self.assertTrue(TITLE.match(produced), f'not a title: {produced!r}')
        return produced

    def test_official_examples(self):
        self.assertEqual(self.check(1), 'A')
        self.assertEqual(self.check(28), 'AB')
        self.assertEqual(self.check(701), 'ZY')
        self.assertEqual(self.solve(1), 'A')
        self.assertEqual(self.solve(28), 'AB')
        self.assertEqual(self.solve(701), 'ZY')

    def test_single_letters(self):
        for n in range(1, 27):
            with self.subTest(n=n):
                self.assertEqual(self.check(n), chr(ord('A') + n - 1))

    def test_carry_boundaries(self):
        # The 'Z' -> 'AA' carry and the equivalents at the end of each block.
        expected = {
            26: 'Z', 27: 'AA', 52: 'AZ', 53: 'BA', 78: 'BZ', 79: 'CA',
            702: 'ZZ', 703: 'AAA', 728: 'AAZ', 729: 'ABA',
            18278: 'ZZZ', 18279: 'AAAA',
        }
        for n, title in expected.items():
            with self.subTest(n=n):
                self.assertEqual(self.check(n), title)
                self.assertEqual(self.inverse(title), n)

    def test_constraint_sized(self):
        # 2^31 - 1 is the constraint maximum and "FXSHRXW" is the largest title.
        self.assertEqual(self.check(MAX_NUMBER), 'FXSHRXW')
        self.assertEqual(self.solve(MAX_NUMBER), 'FXSHRXW')
        self.assertEqual(self.inverse('FXSHRXW'), MAX_NUMBER)
        for n in (MAX_NUMBER - 1, MAX_NUMBER - 26, 26 ** 6, 26 ** 6 + 1,
                  26 ** 6 - 1, 26 ** 7 - 1, 26 ** 7, 1234567890):
            with self.subTest(n=n):
                self.check(n)

    def test_exhaustive_small_numbers(self):
        for n in range(1, 20_001):
            with self.subTest(n=n):
                self.assertEqual(self.solve(n), length_first_oracle(n))

    def test_random_large_numbers(self):
        rng = random.Random(1680)
        for _ in range(2000):
            n = rng.randint(1, MAX_NUMBER)
            with self.subTest(n=n):
                self.check(n)

    def test_round_trip_forward(self):
        # titleToNumber(convertToTitle(n)) == n
        values = list(range(1, 20_001))
        rng = random.Random(1681)
        values += [rng.randint(1, MAX_NUMBER) for _ in range(1000)]
        values += [MAX_NUMBER, MAX_NUMBER - 1, 26, 27, 702, 703, 18278, 18279]
        for n in values:
            with self.subTest(n=n):
                self.assertEqual(self.inverse(self.solve(n)), n)

    def test_round_trip_backward(self):
        # convertToTitle(titleToNumber(t)) == t
        titles = [length_first_oracle(n) for n in range(1, count_up_to(3) + 1)]
        self.assertEqual(len(titles), 18_278)
        self.assertEqual(titles[-1], 'ZZZ')
        rng = random.Random(1682)
        for _ in range(1000):
            titles.append(length_first_oracle(rng.randint(1, MAX_NUMBER)))
        titles += ['FXSHRXW', 'A', 'Z', 'AA', 'ZZ']
        for title in titles:
            with self.subTest(title=title):
                self.assertEqual(self.solve(self.inverse(title)), title)


if __name__ == '__main__':
    unittest.main()
