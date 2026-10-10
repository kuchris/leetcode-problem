import copy
import unittest

from _loader import load_solution

Solution = load_solution('37-sudoku-solver.py').Solution

PUZZLE = [
    ["5", "3", ".", ".", "7", ".", ".", ".", "."],
    ["6", ".", ".", "1", "9", "5", ".", ".", "."],
    [".", "9", "8", ".", ".", ".", ".", "6", "."],
    ["8", ".", ".", ".", "6", ".", ".", ".", "3"],
    ["4", ".", ".", "8", ".", "3", ".", ".", "1"],
    ["7", ".", ".", ".", "2", ".", ".", ".", "6"],
    [".", "6", ".", ".", ".", ".", "2", "8", "."],
    [".", ".", ".", "4", "1", "9", ".", ".", "5"],
    [".", ".", ".", ".", "8", ".", ".", "7", "9"],
]

SOLUTION = [
    ["5", "3", "4", "6", "7", "8", "9", "1", "2"],
    ["6", "7", "2", "1", "9", "5", "3", "4", "8"],
    ["1", "9", "8", "3", "4", "2", "5", "6", "7"],
    ["8", "5", "9", "7", "6", "1", "4", "2", "3"],
    ["4", "2", "6", "8", "5", "3", "7", "9", "1"],
    ["7", "1", "3", "9", "2", "4", "8", "5", "6"],
    ["9", "6", "1", "5", "3", "7", "2", "8", "4"],
    ["2", "8", "7", "4", "1", "9", "6", "3", "5"],
    ["3", "4", "5", "2", "8", "6", "1", "7", "9"],
]

# A puzzle with far fewer givens, to exercise the search rather than a
# nearly-complete grid.
SPARSE_PUZZLE = [
    [".", ".", ".", "2", ".", ".", ".", "6", "3"],
    ["3", ".", ".", ".", ".", "5", "4", ".", "1"],
    [".", ".", "1", ".", ".", "3", "9", "8", "."],
    [".", ".", ".", ".", ".", ".", ".", "9", "."],
    [".", ".", ".", "5", "3", "8", ".", ".", "."],
    [".", "3", ".", ".", ".", ".", ".", ".", "."],
    [".", "2", "6", "3", ".", ".", ".", ".", "."],
    ["5", ".", "3", "7", ".", ".", ".", ".", "8"],
    ["4", "7", ".", ".", ".", "1", ".", ".", "."],
]


def is_complete_and_valid(board) -> bool:
    """Every unit must hold exactly the digits 1-9."""
    digits = set('123456789')
    for index in range(9):
        if set(board[index]) != digits:
            return False
        if {board[r][index] for r in range(9)} != digits:
            return False
    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            cells = {
                board[r][c]
                for r in range(box_row, box_row + 3)
                for c in range(box_col, box_col + 3)
            }
            if cells != digits:
                return False
    return True


def givens_preserved(puzzle, solved) -> bool:
    return all(
        puzzle[r][c] == '.' or puzzle[r][c] == solved[r][c]
        for r in range(9)
        for c in range(9)
    )


class SudokuSolverTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().solveSudoku

    def test_official_example(self):
        board = copy.deepcopy(PUZZLE)
        self.solve(board)
        self.assertEqual(board, SOLUTION)

    def test_sparse_puzzle_is_solved_validly(self):
        board = copy.deepcopy(SPARSE_PUZZLE)
        self.solve(board)
        self.assertTrue(is_complete_and_valid(board))
        self.assertTrue(givens_preserved(SPARSE_PUZZLE, board))

    def test_returns_none_and_mutates_in_place(self):
        board = copy.deepcopy(PUZZLE)
        result = self.solve(board)
        self.assertIsNone(result)
        self.assertEqual(board, SOLUTION)

    def test_already_solved_board_is_unchanged(self):
        board = copy.deepcopy(SOLUTION)
        self.solve(board)
        self.assertEqual(board, SOLUTION)

    def test_every_given_is_still_present(self):
        board = copy.deepcopy(PUZZLE)
        self.solve(board)
        self.assertTrue(givens_preserved(PUZZLE, board))


if __name__ == '__main__':
    unittest.main()
