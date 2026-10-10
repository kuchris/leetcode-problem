import re
import unittest

from _loader import load_solution

Solution = load_solution('8-string-to-integer-atoi.py').Solution

INT_MIN = -(2 ** 31)
INT_MAX = 2 ** 31 - 1
ORACLE = re.compile(r'\s*([+-]?\d+)')


def brute_force(s: str) -> int:
    """Independent oracle: take the leading integer with a regex, then clamp."""
    match = ORACLE.match(s)
    if match is None:
        return 0
    value = int(match.group(1))
    return max(INT_MIN, min(INT_MAX, value))


class StringToIntegerTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().myAtoi

    def test_official_examples(self):
        self.assertEqual(self.solve('42'), 42)
        self.assertEqual(self.solve('   -042'), -42)
        self.assertEqual(self.solve('1337c0d3'), 1337)
        self.assertEqual(self.solve('0-1'), 0)
        self.assertEqual(self.solve('words and 987'), 0)

    def test_empty_and_whitespace_only(self):
        self.assertEqual(self.solve(''), 0)
        self.assertEqual(self.solve('     '), 0)

    def test_sign_handling(self):
        self.assertEqual(self.solve('+1'), 1)
        self.assertEqual(self.solve('-1'), -1)
        # A sign must be immediately followed by digits or a digit run.
        self.assertEqual(self.solve('+-12'), 0)
        self.assertEqual(self.solve('  +  413'), 0)

    def test_stops_at_first_non_digit(self):
        self.assertEqual(self.solve('4193 with words'), 4193)
        self.assertEqual(self.solve('3.14'), 3)
        self.assertEqual(self.solve('00000-42a1234'), 0)

    def test_clamping(self):
        self.assertEqual(self.solve('91283472332'), INT_MAX)
        self.assertEqual(self.solve('-91283472332'), INT_MIN)
        self.assertEqual(self.solve('2147483648'), INT_MAX)
        self.assertEqual(self.solve('-2147483649'), INT_MIN)
        self.assertEqual(self.solve(str(INT_MAX)), INT_MAX)
        self.assertEqual(self.solve(str(INT_MIN)), INT_MIN)

    def test_rejects_non_ascii_digits(self):
        # str.isdigit() would accept superscripts; the solution must not.
        self.assertEqual(self.solve('²'), 0)
        self.assertEqual(self.solve('1²'), 1)

    def test_exhaustive_against_oracle(self):
        pieces = ['', ' ', '   ', '+', '-', '+-', '0', '00', '42', '007', '9' * 12,
                  'a', ' 12a', '-0', '+0', '3.9', 'words', '\t\n 5']
        for first in pieces:
            for second in pieces:
                s = first + second
                with self.subTest(s=s):
                    self.assertEqual(self.solve(s), brute_force(s))


if __name__ == '__main__':
    unittest.main()
