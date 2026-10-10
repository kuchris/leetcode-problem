import itertools
import unittest

from _loader import load_solution

Solution = load_solution('52-n-queens-ii.py').Solution

KNOWN_COUNTS = {1: 1, 2: 0, 3: 0, 4: 2, 5: 10, 6: 4, 7: 40, 8: 92, 9: 352}


def brute_force(n: int) -> int:
    """Try every assignment of one queen per row, checking diagonals directly."""
    count = 0
    for placement in itertools.permutations(range(n)):
        if all(
            abs(placement[i] - placement[j]) != j - i
            for i in range(n)
            for j in range(i + 1, n)
        ):
            count += 1
    return count


class NQueensIITests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().totalNQueens

    def test_official_examples(self):
        self.assertEqual(self.solve(4), 2)
        self.assertEqual(self.solve(1), 1)

    def test_no_solution_sizes(self):
        self.assertEqual(self.solve(2), 0)
        self.assertEqual(self.solve(3), 0)

    def test_exhaustive_against_brute_force(self):
        for n in range(1, 9):
            with self.subTest(n=n):
                self.assertEqual(self.solve(n), brute_force(n))

    def test_known_sequence(self):
        for n in range(1, 10):
            with self.subTest(n=n):
                self.assertEqual(self.solve(n), KNOWN_COUNTS[n])

    def test_returns_an_int(self):
        self.assertIsInstance(self.solve(5), int)

    def test_maximum_size(self):
        self.assertEqual(self.solve(9), 352)


if __name__ == '__main__':
    unittest.main()
