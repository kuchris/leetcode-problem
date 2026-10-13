"""195. Tenth Line -- tests for solutions/195-tenth-line.sh.

The oracle is an independent Python implementation: split the file into lines and
return the tenth when it exists. The script selects the line with a sed address
instead, so agreement is evidence rather than a restatement.

One harness detail matters here: normalise() drops trailing empty lines, so it
cannot tell "printed nothing" from "printed one empty line". The blank-tenth-line
case therefore compares the raw stdout, which is the only place the difference
between those two outcomes is observable.
"""
import unittest

from _shell import normalise, run_script

SOLUTION = '195-tenth-line.sh'


def oracle_lines(text):
    """Independent implementation: the tenth line, or nothing if absent."""
    lines = text.split('\n')
    if lines and lines[-1] == '':
        lines.pop()
    return [lines[9]] if len(lines) >= 10 else []


def numbered_lines(count):
    return '\n'.join(f'Line {position}' for position in range(1, count + 1)) + '\n'


class TenthLineTests(unittest.TestCase):
    def run_case(self, text):
        return normalise(run_script(SOLUTION, {'file.txt': text}))

    def test_official_example(self):
        self.assertEqual(self.run_case(numbered_lines(10)), ['Line 10'])

    def test_fewer_than_ten_lines_prints_nothing(self):
        for count in (0, 1, 2, 5, 9):
            with self.subTest(lines=count):
                self.assertEqual(self.run_case(numbered_lines(count)), [])

    def test_only_the_tenth_line_is_printed(self):
        self.assertEqual(self.run_case(numbered_lines(11)), ['Line 10'])
        self.assertEqual(self.run_case(numbered_lines(200)), ['Line 10'])

    def test_line_ten_without_a_trailing_newline(self):
        text = '\n'.join(f'Line {position}' for position in range(1, 11))
        self.assertEqual(self.run_case(text), ['Line 10'])

    def test_a_blank_tenth_line_is_an_empty_line_not_no_output(self):
        """Raw stdout: nine lines then an empty tenth line."""
        text = '\n'.join(f'Line {position}' for position in range(1, 10)) + '\n\n'
        self.assertEqual(run_script(SOLUTION, {'file.txt': text}), '\n')

    def test_the_other_lines_content_does_not_matter(self):
        lines = [
            '#!/bin/bash', '   spaced   ', '-', '--', 'a b c', '',
            'sed -n 10p', '*', '\\n', 'TENTH',
        ]
        self.assertEqual(self.run_case('\n'.join(lines) + '\n'), ['TENTH'])

    def test_matches_the_oracle_across_many_sizes(self):
        for count in (0, 1, 9, 10, 11, 25, 64):
            with self.subTest(lines=count):
                text = numbered_lines(count)
                self.assertEqual(self.run_case(text), oracle_lines(text))

    def test_large_file(self):
        text = numbered_lines(20000)
        self.assertEqual(self.run_case(text), ['Line 10'])


if __name__ == '__main__':
    unittest.main()
