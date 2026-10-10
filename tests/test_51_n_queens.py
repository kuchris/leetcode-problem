import itertools
import unittest

from _loader import load_solution

Solution = load_solution('51-n-queens.py').Solution

# The number of solutions to the n-queens problem for n = 1..9.
KNOWN_COUNTS = {1: 1, 2: 0, 3: 0, 4: 2, 5: 10, 6: 4, 7: 40, 8: 92, 9: 352}


def is_valid_board(board: list[str]) -> bool:
    """Independently check that no two queens attack each other."""
    n = len(board)
    if any(len(row) != n for row in board):
        return False
    if any(row.count('Q') != 1 for row in board):
        return False
    if any(set(row) - {'.', 'Q'} for row in board):
        return False

    queens = [(r, row.index('Q')) for r, row in enumerate(board)]
    for (r1, c1), (r2, c2) in itertools.combinations(queens, 2):
        if r1 == r2 or c1 == c2 or abs(r1 - r2) == abs(c1 - c2):
            return False
    return True


class NQueensTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().solveNQueens

    def test_official_examples(self):
        self.assertEqual(
            sorted(self.solve(4)),
            sorted([['.Q..', '...Q', 'Q...', '..Q.'], ['..Q.', 'Q...', '...Q', '.Q..']]),
        )
        self.assertEqual(self.solve(1), [['Q']])

    def test_no_solution_sizes(self):
        self.assertEqual(self.solve(2), [])
        self.assertEqual(self.solve(3), [])

    def test_every_returned_board_is_valid(self):
        for n in range(1, 10):
            for board in self.solve(n):
                with self.subTest(n=n, board=board):
                    self.assertTrue(is_valid_board(board))

    def test_solution_counts_match_the_known_sequence(self):
        for n in range(1, 10):
            with self.subTest(n=n):
                self.assertEqual(len(self.solve(n)), KNOWN_COUNTS[n])

    def test_no_duplicate_boards(self):
        for n in range(1, 10):
            boards = self.solve(n)
            with self.subTest(n=n):
                self.assertEqual(len(boards), len({tuple(b) for b in boards}))

    def test_maximum_size(self):
        boards = self.solve(9)
        self.assertEqual(len(boards), 352)
        self.assertTrue(all(is_valid_board(b) for b in boards))


if __name__ == '__main__':
    unittest.main()
