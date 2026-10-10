import itertools
import random
import unittest
from collections import defaultdict

from _loader import load_solution

Solution = load_solution('49-group-anagrams.py').Solution


def brute_force(strs: list[str]) -> list[list[str]]:
    """Group by the sorted word, which is the definition of an anagram."""
    groups = defaultdict(list)
    for word in strs:
        groups[''.join(sorted(word))].append(word)
    return [sorted(group) for group in groups.values()]


def normalise(groups: list[list[str]]) -> list[list[str]]:
    return sorted(sorted(group) for group in groups)


class GroupAnagramsTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().groupAnagrams

    def test_official_examples(self):
        self.assertEqual(
            normalise(self.solve(['eat', 'tea', 'tan', 'ate', 'nat', 'bat'])),
            normalise([['bat'], ['nat', 'tan'], ['ate', 'eat', 'tea']]),
        )
        self.assertEqual(self.solve(['']), [['']])
        self.assertEqual(self.solve(['a']), [['a']])

    def test_empty_strings_group_together(self):
        self.assertEqual(
            normalise(self.solve(['', '', 'a'])), normalise([['', ''], ['a']])
        )

    def test_every_word_is_used_exactly_once(self):
        strs = ['abc', 'bca', 'cab', 'xyz', 'zyx', 'q']
        result = self.solve(strs)
        self.assertEqual(sorted(w for group in result for w in group), sorted(strs))

    def test_all_distinct_words(self):
        self.assertEqual(
            normalise(self.solve(['a', 'b', 'c'])), normalise([['a'], ['b'], ['c']])
        )

    def test_maximum_input(self):
        # 10002 words, each 100 characters, drawn from three anagram families.
        strs = ['a' * 100, 'a' * 99 + 'b', 'a' * 98 + 'bb'] * 3334
        result = self.solve(strs)
        self.assertEqual(len(result), 3)
        self.assertEqual(sum(len(group) for group in result), len(strs))

    def test_exhaustive_small_cases(self):
        pool = ['a', 'b', 'ab', 'ba', 'aa', '', 'abc', 'cba', 'cab']
        for size in range(1, 5):
            for strs in itertools.product(pool, repeat=size):
                with self.subTest(strs=strs):
                    self.assertEqual(
                        normalise(self.solve(list(strs))),
                        normalise(brute_force(list(strs))),
                    )

    def test_randomised_cases(self):
        rng = random.Random(49)
        for _ in range(50):
            strs = [
                ''.join(rng.choice('abc') for _ in range(rng.randint(0, 5)))
                for _ in range(rng.randint(1, 30))
            ]
            with self.subTest(strs=strs):
                self.assertEqual(
                    normalise(self.solve(list(strs))),
                    normalise(brute_force(list(strs))),
                )


if __name__ == '__main__':
    unittest.main()
