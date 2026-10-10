import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('71-simplify-path.py').Solution


def brute_force(path: str) -> str:
    """Independent walker driven by an explicit token list."""
    tokens = []
    buffer = ''
    for char in path + '/':
        if char == '/':
            tokens.append(buffer)
            buffer = ''
        else:
            buffer += char

    result: list[str] = []
    for token in tokens:
        if token in ('', '.'):
            continue
        if token == '..':
            if result:
                result = result[:-1]
            continue
        result.append(token)
    return '/' + '/'.join(result)


class SimplifyPathTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().simplifyPath

    def test_official_examples(self):
        self.assertEqual(self.solve('/home/'), '/home')
        self.assertEqual(self.solve('/home//foo/'), '/home/foo')
        self.assertEqual(self.solve('/home/user/Documents/../Pictures'), '/home/user/Pictures')
        self.assertEqual(self.solve('/../'), '/')
        self.assertEqual(self.solve('/.../a/../b/c/../d/./'), '/.../b/d')

    def test_root_only(self):
        self.assertEqual(self.solve('/'), '/')
        self.assertEqual(self.solve('//'), '/')
        self.assertEqual(self.solve('/./'), '/')

    def test_parent_beyond_root_is_ignored(self):
        self.assertEqual(self.solve('/../..'), '/')
        self.assertEqual(self.solve('/a/../../b'), '/b')

    def test_dots_of_length_three_or_more_are_names(self):
        self.assertEqual(self.solve('/...'), '/...')
        self.assertEqual(self.solve('/..../..'), '/')
        self.assertEqual(self.solve('/.hidden'), '/.hidden')

    def test_trailing_and_repeated_slashes(self):
        self.assertEqual(self.solve('/a/b/c/'), '/a/b/c')
        self.assertEqual(self.solve('/a///b////c'), '/a/b/c')

    def test_underscores_and_digits_are_names(self):
        self.assertEqual(self.solve('/a_1/b2'), '/a_1/b2')

    def test_maximum_length(self):
        path = '/' + 'a/' * 1500
        self.assertEqual(self.solve(path), '/' + '/'.join(['a'] * 1500))

    def test_exhaustive_small_paths(self):
        pieces = ['', '.', '..', 'a', '...', 'b']
        for size in range(1, 5):
            for combination in itertools.product(pieces, repeat=size):
                path = '/' + '/'.join(combination) + '/'
                with self.subTest(path=path):
                    self.assertEqual(self.solve(path), brute_force(path))

    def test_randomised_paths(self):
        rng = random.Random(71)
        for _ in range(400):
            pieces = [rng.choice(['', '.', '..', 'a', 'bb', '...', '_x'])
                      for _ in range(rng.randint(1, 8))]
            separator = lambda: '/' * rng.randint(1, 3)
            path = '/' + ''.join(piece + separator() for piece in pieces)
            with self.subTest(path=path):
                self.assertEqual(self.solve(path), brute_force(path))


if __name__ == '__main__':
    unittest.main()
