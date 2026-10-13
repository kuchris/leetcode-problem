"""194. Transpose File -- tests for solutions/194-transpose-file.sh.

The oracle is an independent Python transpose: split every line on the single
space the statement promises, then read the grid column by column. The script
accumulates one string per column inside awk instead, so the agreement of the two
is evidence rather than a restatement.

The oracle refuses a case whose rows are not all equally wide: the statement
guarantees they are, there is no defined answer for the other shape, and an
arbitrary oracle answer would not be evidence. Every grid below obeys the
guarantee.
"""
import random
import unittest

from _shell import normalise, run_script

SOLUTION = '194-transpose-file.sh'


def oracle_lines(text):
    """Independent implementation: read the grid column by column."""
    rows = [line.split(' ') for line in text.split('\n') if line != '']
    if not rows:
        return []
    width = len(rows[0])
    for row in rows:
        if len(row) != width:
            raise AssertionError(f'case violates the equal-column guarantee: {rows!r}')
    return [' '.join(row[column] for row in rows) for column in range(width)]


def grid_text(grid):
    return '\n'.join(' '.join(row) for row in grid)


def random_grid(rng, height, width):
    return [
        [f'{rng.randrange(100000):05d}' for _ in range(width)] for _ in range(height)
    ]


class TransposeFileTests(unittest.TestCase):
    def run_case(self, text):
        return normalise(run_script(SOLUTION, {'file.txt': text}))

    def test_official_example(self):
        text = 'name age\nalice 21\nryan 30\n'
        self.assertEqual(self.run_case(text), ['name alice ryan', 'age 21 30'])

    def test_single_row(self):
        self.assertEqual(self.run_case('name age\n'), ['name', 'age'])

    def test_single_column(self):
        self.assertEqual(self.run_case('name\nalice\nryan\n'), ['name alice ryan'])

    def test_one_field(self):
        self.assertEqual(self.run_case('solo\n'), ['solo'])

    def test_empty_file_prints_nothing(self):
        self.assertEqual(self.run_case(''), [])

    def test_matches_the_oracle_on_grids_of_many_shapes(self):
        rng = random.Random(194)
        shapes = [(1, 1), (1, 6), (6, 1), (3, 3), (4, 7), (8, 2), (2, 8), (12, 5)]
        for height, width in shapes:
            with self.subTest(shape=(height, width)):
                grid = random_grid(rng, height, width)
                text = grid_text(grid) + '\n'
                self.assertEqual(self.run_case(text), oracle_lines(text))

    def test_single_space_separated_words_survive(self):
        text = 'a b c\nd e f\n'
        self.assertEqual(self.run_case(text), ['a d', 'b e', 'c f'])

    def test_a_wide_grid(self):
        rng = random.Random(1940)
        grid = random_grid(rng, 200, 40)
        text = grid_text(grid) + '\n'
        self.assertEqual(self.run_case(text), oracle_lines(text))

    def test_a_tall_grid(self):
        rng = random.Random(1941)
        grid = random_grid(rng, 500, 3)
        text = grid_text(grid) + '\n'
        self.assertEqual(self.run_case(text), oracle_lines(text))

    def test_file_without_a_trailing_newline(self):
        text = 'name age\nalice 21\nryan 30'
        self.assertEqual(self.run_case(text), ['name alice ryan', 'age 21 30'])

    def test_transposing_twice_returns_the_original_rows(self):
        """An algebraic property of the operation, independent of the oracle."""
        rng = random.Random(1942)
        grid = random_grid(rng, 9, 4)
        text = grid_text(grid) + '\n'
        once = run_script(SOLUTION, {'file.txt': text})
        twice = run_script(SOLUTION, {'file.txt': once})
        self.assertEqual(normalise(twice), [line for line in text.split('\n') if line])


if __name__ == '__main__':
    unittest.main()
