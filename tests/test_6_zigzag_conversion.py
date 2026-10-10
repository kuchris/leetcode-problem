import itertools
import unittest

from _loader import load_solution

Solution = load_solution('6-zigzag-conversion.py').Solution


def brute_force(s: str, num_rows: int) -> str:
    """Build the actual zigzag grid, then read it row by row."""
    if num_rows == 1:
        return s
    rows: list[list[str]] = [[] for _ in range(num_rows)]
    row, step = 0, 1
    for char in s:
        rows[row].append(char)
        if row == num_rows - 1:
            step = -1
        elif row == 0:
            step = 1
        row += step
    return ''.join(''.join(r) for r in rows)


class ZigzagConversionTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().convert

    def test_official_examples(self):
        self.assertEqual(self.solve('PAYPALISHIRING', 3), 'PAHNAPLSIIGYIR')
        self.assertEqual(self.solve('PAYPALISHIRING', 4), 'PINALSIGYAHRPI')
        self.assertEqual(self.solve('A', 1), 'A')

    def test_single_row_is_identity(self):
        self.assertEqual(self.solve('ABCDEFGH', 1), 'ABCDEFGH')

    def test_rows_at_least_length(self):
        # Every character sits on its own row, so the order never changes.
        self.assertEqual(self.solve('ABCD', 4), 'ABCD')
        self.assertEqual(self.solve('ABCD', 1000), 'ABCD')

    def test_maximum_size(self):
        s = 'AB' * 500
        # numRows >= len(s) means every character sits on its own row.
        self.assertEqual(self.solve(s, 1000), s)
        # One row short of that, the tail of the string folds back upwards.
        self.assertEqual(self.solve(s, 999), brute_force(s, 999))

    def test_exhaustive_small_cases(self):
        for size in range(1, 7):
            for letters in itertools.product('ab', repeat=size):
                s = ''.join(letters)
                for num_rows in range(1, 6):
                    with self.subTest(s=s, numRows=num_rows):
                        self.assertEqual(
                            self.solve(s, num_rows), brute_force(s, num_rows)
                        )


if __name__ == '__main__':
    unittest.main()
