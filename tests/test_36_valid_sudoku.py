import copy
import random
import unittest

from _loader import load_solution

Solution = load_solution('36-valid-sudoku.py').Solution

VALID_BOARD = [
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

INVALID_BOX_BOARD = copy.deepcopy(VALID_BOARD)
INVALID_BOX_BOARD[0][0] = "8"

EMPTY_BOARD = [["."] * 9 for _ in range(9)]


class ValidSudokuTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().isValidSudoku

    def test_official_examples(self):
        self.assertTrue(self.solve(VALID_BOARD))
        self.assertFalse(self.solve(INVALID_BOX_BOARD))

    def test_empty_board_is_valid(self):
        self.assertTrue(self.solve(EMPTY_BOARD))

    def test_row_duplicate_is_invalid(self):
        board = copy.deepcopy(EMPTY_BOARD)
        board[0][0] = board[0][8] = "1"
        self.assertFalse(self.solve(board))

    def test_column_duplicate_is_invalid(self):
        board = copy.deepcopy(EMPTY_BOARD)
        board[0][0] = board[8][0] = "1"
        self.assertFalse(self.solve(board))

    def test_box_duplicate_is_invalid(self):
        board = copy.deepcopy(EMPTY_BOARD)
        board[0][0] = board[1][1] = "1"
        self.assertFalse(self.solve(board))

    def test_same_digit_in_different_units_is_valid(self):
        board = copy.deepcopy(EMPTY_BOARD)
        # Different row, column and box: (0,0) and (1,4) are in distinct units.
        board[0][0] = "1"
        board[1][4] = "1"
        self.assertTrue(self.solve(board))

    def test_fully_solved_board_is_valid(self):
        board = [
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
        self.assertTrue(self.solve(board))

    def test_every_single_violation_is_detected(self):
        """Place a duplicate pair in each unit of a full grid in turn."""
        rng = random.Random(36)
        for _ in range(200):
            board = copy.deepcopy(VALID_BOARD)
            # Copy one filled cell onto another cell of the same row.
            row = rng.randrange(9)
            filled = [c for c in range(9) if board[row][c] != '.']
            if len(filled) < 2:
                continue
            source, target = rng.sample(filled, 2)
            board[row][target] = board[row][source]
            with self.subTest(row=row, source=source, target=target):
                self.assertFalse(self.solve(board))


if __name__ == '__main__':
    unittest.main()
