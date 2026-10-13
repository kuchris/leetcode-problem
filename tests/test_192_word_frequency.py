"""192. Word Frequency -- tests for solutions/192-word-frequency.sh.

The oracle is an independent Python implementation of the same transformation:
split the file into whitespace-separated words, count them, and print
``word count`` ordered by count descending. The script does it with
tr/grep/sort/uniq/awk, a different mechanism, so agreement is evidence rather
than a restatement of the script.

The statement guarantees the counts are all different ("Don't worry about
handling ties, it is guaranteed that each word's frequency count is unique"), so
for cases of that shape the output order is fully determined and is compared line
by line. The ties the guarantee excludes are compared as a multiset instead,
which is all the statement promises there.
"""
import random
import unittest
from collections import Counter

from _shell import normalise, run_script

SOLUTION = '192-word-frequency.sh'
LETTERS = 'abcdefghijklmnopqrstuvwxyz'


def oracle_lines(text):
    """Independent implementation of the transformation the statement defines."""
    counts = Counter(text.split())
    return [
        f'{word} {count}'
        for word, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]


def letter_word(index):
    """A unique lowercase word for ``index`` -- base 26, letters only.

    The statement only permits lowercase letters in a word, so a counter based on
    digits (`w0`, `w1`, ...) would be outside the input it promises.
    """
    word = ''
    index += 1
    while index:
        index, remainder = divmod(index - 1, len(LETTERS))
        word = LETTERS[remainder] + word
    return word


def unique_count_text(count):
    """Text with ``count`` distinct words whose frequencies are all different.

    Word i appears i + 1 times, so the frequencies are 1..count: exactly the shape
    the statement guarantees, which makes the expected order unique.
    """
    return ' '.join(
        word for position in range(count) for word in [letter_word(position)] * (position + 1)
    )


class WordFrequencyTests(unittest.TestCase):
    def run_case(self, text):
        return normalise(run_script(SOLUTION, {'words.txt': text}))

    def test_official_example(self):
        text = 'the day is sunny the the\nthe sunny is is\n'
        self.assertEqual(self.run_case(text), ['the 4', 'is 3', 'sunny 2', 'day 1'])

    def test_single_word(self):
        self.assertEqual(self.run_case('hello\n'), ['hello 1'])
        self.assertEqual(self.run_case('hello hello hello'), ['hello 3'])

    def test_words_may_be_separated_by_runs_of_spaces_and_newlines(self):
        """The statement allows one or more whitespace characters between words."""
        text = '  alpha   beta  \n\ngamma\t \nalpha\ngamma gamma\n'
        self.assertEqual(self.run_case(text), ['gamma 3', 'alpha 2', 'beta 1'])

    def test_matches_the_oracle_line_by_line_on_unique_count_input(self):
        cases = [
            'one\n',
            'a aa a aa a\n',
            'the the the fox fox dog\n',
            unique_count_text(20),
        ]
        for text in cases:
            with self.subTest(text=text[:40]):
                self.assertEqual(self.run_case(text), oracle_lines(text))

    def test_counts_are_printed_in_descending_order(self):
        text = unique_count_text(120)
        lines = self.run_case(text)
        counts = [int(line.rsplit(' ', 1)[1]) for line in lines]
        self.assertEqual(len(lines), 120)
        self.assertEqual(counts, sorted(counts, reverse=True))
        # Every line carries the frequency the oracle computed for that word.
        self.assertEqual(
            dict((line.rsplit(' ', 1)[0], int(line.rsplit(' ', 1)[1])) for line in lines),
            dict((word, count) for word, count in Counter(text.split()).items()),
        )

    def test_a_tie_is_printed_once_per_word(self):
        """Outside the statement's guarantee: only the multiset of lines is fixed."""
        text = 'beta alpha beta alpha gamma\n'
        lines = self.run_case(text)
        self.assertEqual(sorted(lines), sorted(oracle_lines(text)))
        self.assertEqual(len(lines), 3)
        # The script picks a fixed order rather than leaving it to the environment.
        self.assertEqual(lines, self.run_case(text))

    def test_empty_and_whitespace_only_files(self):
        for text in ('', '\n', '   \n\t\n  '):
            with self.subTest(text=repr(text)):
                self.assertEqual(self.run_case(text), [])

    def test_large_file(self):
        text = unique_count_text(400)
        self.assertEqual(self.run_case(text), oracle_lines(text))

    def test_words_that_share_a_prefix_are_not_merged(self):
        text = 'ab abc ab abcd abc ab\n'
        self.assertEqual(self.run_case(text), oracle_lines(text))

    def test_repeated_runs_of_the_same_word_across_lines(self):
        rng = random.Random(192)
        words = [letter_word(rng.randrange(40)) for _ in range(500)]
        text = '\n'.join(
            ' '.join(words[position:position + 25]) for position in range(0, 500, 25)
        )
        # Counts may collide here, so compare as a multiset, as the guarantee would
        # not cover this case.
        self.assertEqual(sorted(self.run_case(text)), sorted(oracle_lines(text)))


if __name__ == '__main__':
    unittest.main()
