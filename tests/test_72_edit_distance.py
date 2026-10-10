import itertools
import random
import unittest
from functools import cache

from _loader import load_solution

Solution = load_solution('72-edit-distance.py').Solution


def brute_force(word1: str, word2: str) -> int:
    """Top-down recursion, a different formulation from the rolling DP."""

    @cache
    def distance(i: int, j: int) -> int:
        if i == 0:
            return j
        if j == 0:
            return i
        if word1[i - 1] == word2[j - 1]:
            return distance(i - 1, j - 1)
        return 1 + min(distance(i - 1, j - 1), distance(i - 1, j), distance(i, j - 1))

    return distance(len(word1), len(word2))


class EditDistanceTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().minDistance

    def test_official_examples(self):
        self.assertEqual(self.solve('horse', 'ros'), 3)
        self.assertEqual(self.solve('intention', 'execution'), 5)

    def test_empty_strings(self):
        self.assertEqual(self.solve('', ''), 0)
        self.assertEqual(self.solve('abc', ''), 3)
        self.assertEqual(self.solve('', 'abc'), 3)

    def test_identical_strings(self):
        self.assertEqual(self.solve('abc', 'abc'), 0)
        self.assertEqual(self.solve('a' * 100, 'a' * 100), 0)

    def test_single_character_differences(self):
        self.assertEqual(self.solve('a', 'b'), 1)
        self.assertEqual(self.solve('ab', 'ba'), 2)

    def test_one_is_a_subsequence_of_the_other(self):
        self.assertEqual(self.solve('abcde', 'ace'), 2)
        self.assertEqual(self.solve('ace', 'abcde'), 2)

    def test_maximum_length(self):
        rng = random.Random(72)
        word1 = ''.join(rng.choice('abc') for _ in range(500))
        word2 = ''.join(rng.choice('abc') for _ in range(500))
        self.assertEqual(self.solve(word1, word2), brute_force(word1, word2))

    def test_exhaustive_small_cases(self):
        strings = ['']
        for size in range(1, 5):
            strings += [''.join(c) for c in itertools.product('ab', repeat=size)]
        for word1 in strings:
            for word2 in strings:
                with self.subTest(word1=word1, word2=word2):
                    self.assertEqual(self.solve(word1, word2), brute_force(word1, word2))

    def test_randomised_cases(self):
        rng = random.Random(720)
        for _ in range(200):
            word1 = ''.join(rng.choice('abcd') for _ in range(rng.randint(0, 12)))
            word2 = ''.join(rng.choice('abcd') for _ in range(rng.randint(0, 12)))
            with self.subTest(word1=word1, word2=word2):
                self.assertEqual(self.solve(word1, word2), brute_force(word1, word2))


if __name__ == '__main__':
    unittest.main()
