import itertools
import unittest

from _loader import load_solution

Solution = load_solution('58-length-of-last-word.py').Solution


def brute_force(s: str) -> int:
    return len(s.split()[-1])


class LengthOfLastWordTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().lengthOfLastWord

    def test_official_examples(self):
        self.assertEqual(self.solve('Hello World'), 5)
        self.assertEqual(self.solve('   fly me   to   the moon  '), 4)
        self.assertEqual(self.solve('luffy is still joyboy'), 6)

    def test_single_word(self):
        self.assertEqual(self.solve('a'), 1)
        self.assertEqual(self.solve('word'), 4)

    def test_leading_and_trailing_spaces(self):
        self.assertEqual(self.solve('   a   '), 1)
        self.assertEqual(self.solve('a b'), 1)

    def test_multiple_trailing_spaces(self):
        self.assertEqual(self.solve('abc      '), 3)

    def test_maximum_length(self):
        s = 'a' * 9999 + ' ' + 'b' * 9999
        self.assertEqual(self.solve(s), 9999)
        self.assertEqual(self.solve(' ' * 9999 + 'abc'), 3)

    def test_exhaustive_small_cases(self):
        for size in range(1, 9):
            for chars in itertools.product('ab ', repeat=size):
                s = ''.join(chars)
                if not s.split():
                    continue  # the statement guarantees at least one word
                with self.subTest(s=s):
                    self.assertEqual(self.solve(s), brute_force(s))


if __name__ == '__main__':
    unittest.main()
