"""Tests for 151. Reverse Words in a String.

Two independent oracles:

  - `regex_oracle` tokenises with `re.findall(r'\\S+', s)` and joins in reverse;
  - `in_place_oracle` is the follow-up algorithm the statement asks about: it
    copies the string into a mutable buffer, reverses the whole buffer, reverses
    each word inside it, and then compacts the runs of spaces with a write
    pointer. It shares no code with the solution or with the regex oracle.

The statement guarantees letters, digits and single spaces with at least one word,
so the exhaustive sweep uses `{'a', 'b', ' '}` and skips the all-space strings --
those are not valid inputs because s always contains a word.
"""

import itertools
import random
import re
import unittest

from _loader import load_solution

Solution = load_solution('151-reverse-words-in-a-string.py').Solution

OUTPUT_ALPHABET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'


def regex_oracle(s: str) -> str:
    return ' '.join(reversed(re.findall(r'\S+', s)))


def in_place_oracle(s: str) -> str:
    """Reverse-all, reverse-each-word, compact-spaces on a mutable buffer."""
    buffer = list(s)
    buffer.reverse()

    length = len(buffer)
    index = 0
    while index < length:
        if buffer[index] == ' ':
            index += 1
            continue
        start = index
        while index < length and buffer[index] != ' ':
            index += 1
        buffer[start:index] = reversed(buffer[start:index])

    write = 0
    read = 0
    while read < length:
        if buffer[read] == ' ':
            read += 1
            continue
        if write:
            buffer[write] = ' '
            write += 1
        while read < length and buffer[read] != ' ':
            buffer[write] = buffer[read]
            write += 1
            read += 1

    return ''.join(buffer[:write])


class ReverseWordsInAStringTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().reverseWords

    def assert_matches(self, s: str) -> str:
        result = self.solve(s)
        expected = regex_oracle(s)

        self.assertEqual(result, expected, f'input {s!r}')
        self.assertEqual(self.solve(s), in_place_oracle(s), f'input {s!r}')
        # Output shape: no leading/trailing space, exactly one space per gap.
        self.assertNotEqual(result, '')
        self.assertEqual(result, result.strip())
        self.assertNotIn('  ', result)
        self.assertEqual(sorted(result.split(' ')), sorted(expected.split(' ')))
        return result

    def test_official_examples(self):
        self.assertEqual(self.solve('the sky is blue'), 'blue is sky the')
        self.assertEqual(self.solve('  hello world  '), 'world hello')
        self.assertEqual(self.solve('a good   example'), 'example good a')

    def test_single_word(self):
        self.assertEqual(self.solve('a'), 'a')
        self.assertEqual(self.solve('word'), 'word')
        self.assertEqual(self.solve('   word   '), 'word')
        self.assertEqual(self.solve('   word'), 'word')
        self.assertEqual(self.solve('word   '), 'word')

    def test_two_words(self):
        self.assertEqual(self.solve('a b'), 'b a')
        self.assertEqual(self.solve('a  b'), 'b a')
        self.assertEqual(self.solve('  a  b  '), 'b a')

    def test_digits_upper_and_lower_case(self):
        self.assertEqual(self.solve('Hello World 123'), '123 World Hello')
        self.assertEqual(self.solve('a1 A2'), 'A2 a1')
        self.assert_matches('AbC 12 xYz   9')

    def test_already_reversed(self):
        self.assertEqual(self.solve('c b a'), 'a b c')
        self.assertEqual(self.solve('c  b  a'), 'a b c')

    def test_all_spaces_between_single_letters(self):
        self.assertEqual(self.solve('a   b   c   d'), 'd c b a')
        self.assertEqual(self.solve(' a  b '), 'b a')

    def test_exhaustive_small_strings(self):
        checked = 0
        for length in range(1, 8):
            for chars in itertools.product('ab ', repeat=length):
                s = ''.join(chars)
                if not s.strip():
                    continue  # the statement guarantees at least one word
                with self.subTest(s=s):
                    self.assert_matches(s)
                checked += 1
        self.assertGreater(checked, 2000)

    def test_exhaustive_single_word_with_padding(self):
        for word_length in range(1, 5):
            for chars in itertools.product('ab', repeat=word_length):
                word = ''.join(chars)
                for before in range(4):
                    for after in range(4):
                        s = ' ' * before + word + ' ' * after
                        with self.subTest(s=s):
                            self.assertEqual(self.solve(s), word)

    def test_randomised_strings(self):
        rng = random.Random(1510)
        for _ in range(400):
            words = [
                ''.join(rng.choice(OUTPUT_ALPHABET) for _ in range(rng.randint(1, 6)))
                for _ in range(rng.randint(1, 8))
            ]
            gaps = [rng.choice([' ', '  ', '   ', '    ']) for _ in range(len(words) - 1)]
            s = (' ' * rng.randint(0, 3)) + words[0]
            for gap, word in zip(gaps, words[1:]):
                s += gap + word
            s += ' ' * rng.randint(0, 3)
            with self.subTest(s=s):
                self.assertEqual(self.solve(s), ' '.join(reversed(words)))

    def test_randomised_against_both_oracles(self):
        rng = random.Random(1511)
        for _ in range(300):
            length = rng.randint(1, 30)
            s = ''.join(rng.choice('ab12 ') for _ in range(length))
            if not s.strip():
                s += 'z'
            with self.subTest(s=s):
                self.assert_matches(s)

    def test_constraint_sized(self):
        # 10^4 characters is the constraint maximum.
        words = ['a'] * 3334
        s = ' ' * (10000 - (len(words) + len(words) - 1)) + ' '.join(words)
        self.assertEqual(len(s), 10000)
        self.assertEqual(self.solve(s), ' '.join(reversed(words)))
        self.assertEqual(self.solve(s), regex_oracle(s))

        # Maximal single word, padded out to 10^4 characters.
        long_word = 'a' * 5000
        padded = ' ' * 4998 + long_word + ' ' + 'b'
        self.assertEqual(len(padded), 10000)
        self.assertEqual(self.solve(padded), 'b ' + long_word)

    def test_constraint_sized_random(self):
        rng = random.Random(1512)
        for _ in range(5):
            words = [''.join(rng.choice('abZ9') for _ in range(rng.randint(1, 9))) for _ in range(1200)]
            s = '  '.join(words)
            s = s[:10000]
            if s.endswith(' '):
                s = s[:-1] + 'z'
            self.assertLessEqual(len(s), 10000)
            with self.subTest(length=len(s)):
                self.assertEqual(self.solve(s), regex_oracle(s))
                self.assertEqual(self.solve(s), in_place_oracle(s))


if __name__ == '__main__':
    unittest.main()
