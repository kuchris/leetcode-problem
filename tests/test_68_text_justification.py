import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('68-text-justification.py').Solution


def brute_force(words: list[str], max_width: int) -> list[str]:
    """Independent formatter built from explicit line grouping."""
    lines = []
    current: list[str] = []
    for word in words:
        candidate = current + [word]
        needed = sum(len(w) for w in candidate) + len(candidate) - 1
        if needed <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = [word]
    if current:
        lines.append(current)

    output = []
    for index, line in enumerate(lines):
        is_last = index == len(lines) - 1
        if is_last or len(line) == 1:
            output.append(' '.join(line).ljust(max_width))
            continue
        slots = len(line) - 1
        spaces = max_width - sum(len(w) for w in line)
        per_slot, remainder = divmod(spaces, slots)
        rendered = ''
        for position, word in enumerate(line):
            rendered += word
            if position < slots:
                rendered += ' ' * (per_slot + (1 if position < remainder else 0))
        output.append(rendered)
    return output


class TextJustificationTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().fullJustify

    def test_official_examples(self):
        self.assertEqual(
            self.solve(['This', 'is', 'an', 'example', 'of', 'text', 'justification.'], 16),
            ['This    is    an', 'example  of text', 'justification.  '],
        )
        self.assertEqual(
            self.solve(['What', 'must', 'be', 'acknowledgment', 'shall', 'be'], 16),
            ['What   must   be', 'acknowledgment  ', 'shall be        '],
        )
        self.assertEqual(
            self.solve(
                ['Science', 'is', 'what', 'we', 'understand', 'well', 'enough',
                 'to', 'explain', 'to', 'a', 'computer.', 'Art', 'is',
                 'everything', 'else', 'we', 'do'], 20,
            ),
            ['Science  is  what we', 'understand      well', 'enough to explain to',
             'a  computer.  Art is', 'everything  else  we', 'do                  '],
        )

    def test_every_line_has_exactly_max_width(self):
        rng = random.Random(68)
        for _ in range(100):
            max_width = rng.randint(1, 20)
            words = [
                ''.join(rng.choice('abc') for _ in range(rng.randint(1, max_width)))
                for _ in range(rng.randint(1, 15))
            ]
            for line in self.solve(words, max_width):
                with self.subTest(words=words, maxWidth=max_width):
                    self.assertEqual(len(line), max_width)

    def test_words_survive_in_order(self):
        rng = random.Random(680)
        for _ in range(100):
            max_width = rng.randint(1, 20)
            words = [
                ''.join(rng.choice('abc') for _ in range(rng.randint(1, max_width)))
                for _ in range(rng.randint(1, 15))
            ]
            rendered = self.solve(words, max_width)
            recovered = [w for line in rendered for w in line.split()]
            with self.subTest(words=words, maxWidth=max_width):
                self.assertEqual(recovered, words)

    def test_single_word_lines_are_left_justified(self):
        self.assertEqual(self.solve(['a'], 5), ['a    '])
        self.assertEqual(self.solve(['abcdefghij'], 10), ['abcdefghij'])

    def test_maximum_input(self):
        words = ['a' * 20] * 300
        rendered = self.solve(words, 100)
        self.assertTrue(all(len(line) == 100 for line in rendered))
        self.assertEqual([w for line in rendered for w in line.split()], words)

    def test_exhaustive_small_cases(self):
        vocabulary = ['a', 'bb', 'ccc', 'dd']
        for size in range(1, 6):
            for words in itertools.product(vocabulary, repeat=size):
                for max_width in range(max(len(w) for w in words), 9):
                    with self.subTest(words=words, maxWidth=max_width):
                        self.assertEqual(
                            self.solve(list(words), max_width),
                            brute_force(list(words), max_width),
                        )

    def test_randomised_against_oracle(self):
        rng = random.Random(681)
        for _ in range(300):
            max_width = rng.randint(1, 16)
            words = [
                ''.join(rng.choice('abc') for _ in range(rng.randint(1, max_width)))
                for _ in range(rng.randint(1, 12))
            ]
            with self.subTest(words=words, maxWidth=max_width):
                self.assertEqual(
                    self.solve(list(words), max_width), brute_force(list(words), max_width)
                )


if __name__ == '__main__':
    unittest.main()
