"""Tests for 187. Repeated DNA Sequences.

Oracles:
  - ``counter_oracle``: ``collections.Counter`` over every 10-letter window, then
    the keys whose count exceeds 1. It counts occurrences instead of tracking
    first and second sightings, so it does not share the solution's structure.
  - ``pairwise_oracle``: compares every pair of start positions character by
    character — no hashing and no counting at all. O(n^2), used on the small and
    exhaustive cases.

Results are compared as sets because the statement allows any order, and the
returned list is additionally checked for duplicates and for window length.

Exhaustive sweep: every string over {A, C} of length 9..13. Randomly sampled
4-letter strings cover the full alphabet, and the 10^5 constraint cases include
a periodic string whose repeated windows are derived by hand.
"""

import collections
import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('187-repeated-dna-sequences.py').Solution

MAX_LENGTH = 10 ** 5
WINDOW = 10
LETTERS = 'ACGT'


def counter_oracle(s) -> set:
    counts = collections.Counter(
        s[start:start + WINDOW] for start in range(len(s) - WINDOW + 1)
    )
    return {window for window, count in counts.items() if count > 1}


def pairwise_oracle(s) -> set:
    starts = len(s) - WINDOW + 1
    repeated = set()
    for left in range(starts):
        for right in range(left + 1, starts):
            if s[left:left + WINDOW] == s[right:right + WINDOW]:
                repeated.add(s[left:left + WINDOW])
    return repeated


class RepeatedDnaSequencesTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().findRepeatedDnaSequences

    def check(self, s, oracle=counter_oracle):
        result = self.solve(s)
        self.assertEqual(len(result), len(set(result)), 'duplicate windows returned')
        for window in result:
            self.assertEqual(len(window), WINDOW)
        self.assertEqual(set(result), oracle(s))
        return set(result)

    def test_official_examples(self):
        self.assertEqual(
            self.check("AAAAACCCCCAAAAACCCCCCAAAAAGGGTTT"),
            {"AAAAACCCCC", "CCCCCAAAAA"},
        )
        self.assertEqual(self.check("AAAAAAAAAAAAA"), {"AAAAAAAAAA"})

    def test_strings_shorter_than_the_window(self):
        for length in range(1, WINDOW):
            text = ("ACGT" * 3)[:length]
            with self.subTest(length=length):
                self.assertEqual(self.solve(text), [])

    def test_exactly_one_window(self):
        self.assertEqual(self.solve("ACGTACGTAC"), [])
        self.assertEqual(self.solve("A" * WINDOW), [])

    def test_overlapping_occurrences(self):
        # Both windows repeat, and they overlap each other.
        self.assertEqual(self.check("ACACACACACACAC"), {"ACACACACAC", "CACACACACA"})
        # A single 10-mer repeated by sliding one character at a time.
        self.assertEqual(self.check("A" * 14), {"AAAAAAAAAA"})
        self.assertEqual(self.check("AAAAAAAAAAA"), {"AAAAAAAAAA"})

    def test_periodic_strings(self):
        period = "ACGTACGTAC"
        # Two periods give 11 windows: the one at offset 0 and the one at
        # offset 10 are both the period itself, and every other offset occurs
        # exactly once.
        self.assertEqual(self.check(period * 2), {period})
        # Three periods give 21 windows, so every one of the ten rotations
        # occurs at least twice (offsets r, r + 10 and, for r = 0, r + 20).
        rotations = {period[shift:] + period[:shift] for shift in range(WINDOW)}
        self.assertEqual(len(rotations), WINDOW)
        self.assertEqual(self.check(period * 3), rotations)
        self.assertEqual(self.check(period * 4), rotations)

    def test_exhaustive_binary_alphabet(self):
        for length in range(WINDOW - 1, WINDOW + 4):
            for letters in itertools.product("AC", repeat=length):
                text = ''.join(letters)
                with self.subTest(text=text):
                    self.check(text)
                    self.assertEqual(set(self.solve(text)), pairwise_oracle(text))

    def test_random_strings(self):
        rng = random.Random(1870)
        for _ in range(500):
            length = rng.randint(1, 80)
            text = ''.join(rng.choice(LETTERS) for _ in range(length))
            with self.subTest(length=length, head=text[:16]):
                self.check(text)
        for _ in range(200):
            length = rng.randint(WINDOW, 40)
            text = ''.join(rng.choice("AC") for _ in range(length))
            with self.subTest(length=length, head=text[:16]):
                self.assertEqual(set(self.solve(text)), pairwise_oracle(text))

    def test_random_strings_built_from_repeats(self):
        rng = random.Random(1871)
        for _ in range(200):
            motif = ''.join(rng.choice(LETTERS) for _ in range(rng.randint(1, 12)))
            copies = rng.randint(2, 6)
            filler = ''.join(rng.choice(LETTERS) for _ in range(rng.randint(0, 5)))
            text = (motif + filler) * copies
            with self.subTest(motif=motif, copies=copies):
                self.check(text)

    def test_constraint_sized_all_same_letter(self):
        self.assertEqual(self.check("A" * MAX_LENGTH), {"AAAAAAAAAA"})
        self.assertEqual(self.check("C" * MAX_LENGTH), {"CCCCCCCCCC"})

    def test_constraint_sized_random(self):
        rng = random.Random(1872)
        text = ''.join(rng.choice(LETTERS) for _ in range(MAX_LENGTH))
        self.assertEqual(len(text), MAX_LENGTH)
        self.assertEqual(self.check(text), counter_oracle(text))

    def test_constraint_sized_periodic(self):
        period = "ACGTACGTAC"
        text = (period * (MAX_LENGTH // WINDOW + 1))[:MAX_LENGTH]
        rotations = {period[shift:] + period[:shift] for shift in range(WINDOW)}
        self.assertEqual(self.check(text), rotations)
        self.assertEqual(len(self.solve(text)), WINDOW)

    def test_constraint_sized_two_planted_occurrences(self):
        rng = random.Random(1873)
        body = ''.join(rng.choice(LETTERS) for _ in range(MAX_LENGTH - 2 * WINDOW))
        planted = ''.join(rng.choice(LETTERS) for _ in range(WINDOW))
        text = planted + body + planted
        self.assertEqual(len(text), MAX_LENGTH)
        self.assertIn(planted, self.check(text))

        # The same window twice, separated by a long unique middle.
        text = "A" * WINDOW + "C" * (MAX_LENGTH - 2 * WINDOW) + "A" * WINDOW
        result = self.check(text)
        self.assertIn("AAAAAAAAAA", result)


if __name__ == '__main__':
    unittest.main()
