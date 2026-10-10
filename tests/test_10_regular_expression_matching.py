import itertools
import re
import unittest

from _loader import load_solution

Solution = load_solution('10-regular-expression-matching.py').Solution


def brute_force(s: str, p: str) -> bool:
    """Independent oracle: Python's own engine uses the same '.'/'*' semantics."""
    return re.fullmatch(p, s) is not None


def patterns(max_atoms: int):
    """Every valid pattern over {a, b, .} where '*' always follows an atom."""
    atoms = [letter + star for letter in 'ab.' for star in ('', '*')]
    for count in range(1, max_atoms + 1):
        for combination in itertools.product(atoms, repeat=count):
            yield ''.join(combination)


class RegularExpressionMatchingTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().isMatch

    def test_official_examples(self):
        self.assertFalse(self.solve('aa', 'a'))
        self.assertTrue(self.solve('aa', 'a*'))
        self.assertTrue(self.solve('ab', '.*'))

    def test_empty_input(self):
        self.assertTrue(self.solve('', 'c*'))
        self.assertTrue(self.solve('', '.*'))
        self.assertFalse(self.solve('', '.'))
        self.assertFalse(self.solve('a', ''))

    def test_star_spans_multiple_groups(self):
        self.assertTrue(self.solve('aab', 'c*a*b'))
        self.assertFalse(self.solve('mississippi', 'mis*is*p*.'))

    def test_star_matches_zero_repetitions(self):
        self.assertTrue(self.solve('ab', 'a*b'))
        self.assertTrue(self.solve('b', 'a*b'))

    def test_maximum_length_input(self):
        self.assertTrue(self.solve('a' * 20, 'a*'))
        self.assertTrue(self.solve('a' * 20, '.*'))
        self.assertFalse(self.solve('a' * 20, 'a'))

    def test_exhaustive_small_cases(self):
        strings = ['']
        for size in range(1, 5):
            strings += [''.join(c) for c in itertools.product('ab', repeat=size)]
        for p in patterns(3):
            for s in strings:
                with self.subTest(s=s, p=p):
                    self.assertEqual(self.solve(s, p), brute_force(s, p))


if __name__ == '__main__':
    unittest.main()
