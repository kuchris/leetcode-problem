"""193. Valid Phone Numbers -- tests for solutions/193-valid-phone-numbers.sh.

The oracle is an independent Python implementation: split file.txt into lines and
keep those that match the whole line against either ``(xxx) xxx-xxxx`` or
``xxx-xxx-xxxx`` (re.fullmatch, never re.search). The script uses a single
grep -E pattern with ^ and $ anchors, so the two agree for different reasons.

The statement says each line "must not contain leading or trailing white spaces",
so every case here obeys that. The embedded cases are lines such as
"call 987-123-4567 now": no surrounding whitespace, but surrounding text, which
must still be rejected because the number does not occupy the whole line.
"""
import random
import re
import unittest

from _shell import normalise, run_script

SOLUTION = '193-valid-phone-numbers.sh'
VALID = re.compile(r'\(\d{3}\) \d{3}-\d{4}|\d{3}-\d{3}-\d{4}')


def oracle_lines(text):
    """Independent implementation: full-line match, order preserved."""
    return [line for line in text.split('\n') if VALID.fullmatch(line)]


class ValidPhoneNumbersTests(unittest.TestCase):
    def run_case(self, text):
        return normalise(run_script(SOLUTION, {'file.txt': text}))

    def test_official_example(self):
        text = '987-123-4567\n123 456 7890\n(123) 456-7890\n'
        self.assertEqual(self.run_case(text), ['987-123-4567', '(123) 456-7890'])

    def test_a_number_embedded_in_other_text_is_not_valid(self):
        text = '\n'.join([
            'call 987-123-4567 now',
            '987-123-4567 ext 4',
            '(123) 456-7890?',
            'tel:(123) 456-7890',
            'abc (123) 456-7890',
        ])
        self.assertEqual(self.run_case(text + '\n'), [])

    def test_near_misses_are_rejected(self):
        lines = [
            '(123)456-7890',      # the space after the area code is required
            '(123) 4567890',      # missing hyphen
            '(123) 456-789',      # too few digits
            '(123) 456-78901',    # too many digits
            '123-45-6789',        # digits regrouped
            '1234-567-8901',      # too many leading digits
            '123-456-78901',      # too many trailing digits
            '(12) 345-6789',      # two-digit area code
            '(1234) 567-8901',    # four-digit area code
            '987 123 4567',       # spaces instead of hyphens
            '987-123-4567 ',      # trailing space
            ' 987-123-4567',      # leading space
            '(123) 456-7890 (5)', # extra text
            '',                   # empty line
        ]
        self.assertEqual(self.run_case('\n'.join(lines) + '\n'), [])

    def test_no_valid_numbers_prints_nothing(self):
        self.assertEqual(self.run_case('123 456 7890\nnot a number\n'), [])

    def test_output_preserves_input_order_and_repeats(self):
        text = '\n'.join([
            '(111) 222-3333',
            'nope',
            '444-555-6666',
            '(111) 222-3333',
            '(777) 888-9999',
        ])
        self.assertEqual(
            self.run_case(text + '\n'),
            ['(111) 222-3333', '444-555-6666', '(111) 222-3333', '(777) 888-9999'],
        )

    def test_every_valid_line_is_kept(self):
        text = '\n'.join(f'{n:03d}-{n:03d}-{n:04d}' for n in range(1, 51))
        self.assertEqual(self.run_case(text + '\n'), text.split('\n'))

    def test_matches_the_oracle_on_a_generated_corpus(self):
        rng = random.Random(193)
        lines = []
        for index in range(600):
            area, mid, tail = (rng.randrange(1000), rng.randrange(1000), rng.randrange(10000))
            style = index % 5
            if style == 0:
                lines.append(f'({area:03d}) {mid:03d}-{tail:04d}')   # valid
            elif style == 1:
                lines.append(f'{area:03d}-{mid:03d}-{tail:04d}')      # valid
            elif style == 2:
                lines.append(f'call ({area:03d}) {mid:03d}-{tail:04d} x')  # embedded
            elif style == 3:
                lines.append(f'{area:03d} {mid:03d}-{tail:04d}')      # wrong separator
            else:
                lines.append(f'({area:03d}) {mid:03d}{tail:04d}')     # missing hyphen
        text = '\n'.join(lines) + '\n'
        self.assertEqual(self.run_case(text), oracle_lines(text))

    def test_large_file(self):
        rng = random.Random(1930)
        lines = [
            f'{rng.randrange(1000):03d}-{rng.randrange(1000):03d}-{rng.randrange(10000):04d}'
            for _ in range(2000)
        ]
        text = '\n'.join(lines) + '\n'
        self.assertEqual(self.run_case(text), oracle_lines(text))

    def test_file_without_a_trailing_newline(self):
        self.assertEqual(self.run_case('987-123-4567'), ['987-123-4567'])


if __name__ == '__main__':
    unittest.main()
