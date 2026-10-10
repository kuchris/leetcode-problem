"""Tests for 130. Surrounded Regions.

`solve` mutates its argument, so comparing two boards that the solution produced
would hide an in-place mistake. Every test therefore computes
`expected_board(original)` from the untouched input -- with a different algorithm
-- and compares it against a board that was handed to the solution:

  - `expected_board` is a union-find over the cells: adjacent 'O' cells are
    unioned, a component survives exactly when it contains a border cell, and the
    expected board is written from scratch. It never floods from the border the
    way the solution does.

`letter_grids` sweeps every binary grid of up to 3x3, which is where single rows,
single columns, corners and diagonal-only touching are all decided.
"""

import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('130-surrounded-regions.py').Solution


def letter_grid(bits) -> list:
    """Turn a grid of 0/1 (1 = 'O') into a board of letters."""
    return [['O' if cell else 'X' for cell in row] for row in bits]


def copy_board(board) -> list:
    return [list(row) for row in board]


def expected_board(board) -> list:
    rows, cols = len(board), len(board[0])
    parent = list(range(rows * cols))

    def find(cell: int) -> int:
        root = cell
        while parent[root] != root:
            root = parent[root]
        while parent[cell] != root:  # path compression
            parent[cell], cell = root, parent[cell]
        return root

    def union(first: int, second: int) -> None:
        first, second = find(first), find(second)
        if first != second:
            parent[second] = first

    for row in range(rows):
        for col in range(cols):
            if board[row][col] != 'O':
                continue
            if row + 1 < rows and board[row + 1][col] == 'O':
                union(row * cols + col, (row + 1) * cols + col)
            if col + 1 < cols and board[row][col + 1] == 'O':
                union(row * cols + col, row * cols + col + 1)

    safe = set()
    for row in range(rows):
        for col in range(cols):
            if board[row][col] == 'O' and (row in (0, rows - 1) or col in (0, cols - 1)):
                safe.add(find(row * cols + col))

    return [
        ['O' if board[row][col] == 'O' and find(row * cols + col) in safe else 'X' for col in range(cols)]
        for row in range(rows)
    ]


class SurroundedRegionsTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().solve

    def run_solve(self, board) -> list:
        """Run the solution on a copy and return that copy."""
        working = copy_board(board)
        self.assertIsNone(self.solve(working))
        return working

    def test_official_examples(self):
        board = [['X', 'X', 'X', 'X'], ['X', 'O', 'O', 'X'], ['X', 'X', 'O', 'X'], ['X', 'O', 'X', 'X']]
        self.assertEqual(
            self.run_solve(board),
            [['X', 'X', 'X', 'X'], ['X', 'X', 'X', 'X'], ['X', 'X', 'X', 'X'], ['X', 'O', 'X', 'X']],
        )
        self.assertEqual(self.run_solve([['X']]), [['X']])

    def test_mutates_the_given_list_in_place(self):
        board = [['X', 'X', 'X'], ['X', 'O', 'X'], ['X', 'X', 'X']]
        rows = [row for row in board]
        self.assertIsNone(self.solve(board))
        self.assertEqual(len(board), 3)
        self.assertTrue(all(board[index] is rows[index] for index in range(3)))
        self.assertEqual(board, [['X'] * 3 for _ in range(3)])

    def test_single_cell(self):
        self.assertEqual(self.run_solve([['O']]), [['O']])
        self.assertEqual(self.run_solve([['X']]), [['X']])

    def test_single_row_and_column(self):
        # Every cell of a 1 x n or n x 1 board lies on the border.
        row = [['O'] * 5]
        self.assertEqual(self.run_solve(row), [['O'] * 5])
        column = [['O'] for _ in range(5)]
        self.assertEqual(self.run_solve(column), [['O'] for _ in range(5)])
        self.assertEqual(self.run_solve([['O', 'X', 'O']]), [['O', 'X', 'O']])

    def test_fully_surrounded_region_is_captured(self):
        board = [['X'] * 5] + [['X', 'X', 'O', 'X', 'X'], ['X', 'X', 'O', 'X', 'X'], ['X', 'X', 'O', 'X', 'X']] + [['X'] * 5]
        self.assertEqual(self.run_solve(board), [['X'] * 5 for _ in range(5)])

    def test_region_touching_the_border_survives(self):
        board = [['X', 'X', 'X', 'X'], ['O', 'O', 'O', 'X'], ['X', 'X', 'O', 'X'], ['X', 'X', 'X', 'X']]
        self.assertEqual(self.run_solve(board), board)
        corner = [['O', 'X', 'X'], ['X', 'O', 'X'], ['X', 'X', 'O']]
        # The two corner 'O's are on the border; the middle one is not.
        self.assertEqual(self.run_solve(corner), [['O', 'X', 'X'], ['X', 'X', 'X'], ['X', 'X', 'O']])
        self.assertEqual(self.run_solve(corner), expected_board(corner))

    def test_diagonal_touching_does_not_connect(self):
        board = [['X', 'O', 'X', 'X'], ['X', 'X', 'O', 'X'], ['X', 'X', 'X', 'O'], ['X', 'X', 'X', 'X']]
        # (0, 1) and (2, 3) are on the border; (1, 2) is interior and alone.
        self.assertEqual(
            self.run_solve(board),
            [['X', 'O', 'X', 'X'], ['X', 'X', 'X', 'X'], ['X', 'X', 'X', 'O'], ['X', 'X', 'X', 'X']],
        )
        self.assertEqual(self.run_solve(board), expected_board(board))
        inner = [['X', 'X', 'X', 'X'], ['X', 'O', 'X', 'X'], ['X', 'X', 'O', 'X'], ['X', 'X', 'X', 'X']]
        self.assertEqual(self.run_solve(inner), [['X'] * 4 for _ in range(4)])

    def test_one_cell_gap_keeps_the_diagonal_apart(self):
        board = [['X', 'X', 'X', 'X', 'X'], ['X', 'O', 'X', 'O', 'X'], ['X', 'X', 'X', 'X', 'X']]
        self.assertEqual(self.run_solve(board), [['X'] * 5 for _ in range(3)])

    def test_exhaustive_small_grids(self):
        for rows, cols in ((1, 1), (1, 2), (2, 1), (1, 3), (3, 1), (2, 2), (2, 3), (3, 2), (3, 3)):
            for bits in itertools.product((0, 1), repeat=rows * cols):
                grid = [list(bits[index * cols:(index + 1) * cols]) for index in range(rows)]
                board = letter_grid(grid)
                with self.subTest(rows=rows, cols=cols, bits=bits):
                    self.assertEqual(self.run_solve(board), expected_board(board))

    def test_randomised_grids(self):
        rng = random.Random(1300)
        for _ in range(400):
            rows = rng.randint(1, 8)
            cols = rng.randint(1, 8)
            board = [[rng.choice('XO') for _ in range(cols)] for _ in range(rows)]
            with self.subTest(rows=rows, cols=cols, board=board):
                self.assertEqual(self.run_solve(board), expected_board(board))

    def test_randomised_biased_grids(self):
        # Heavily 'O'-biased grids produce large regions that touch no border.
        rng = random.Random(1301)
        for _ in range(200):
            rows = rng.randint(3, 12)
            cols = rng.randint(3, 12)
            board = [[rng.choices('XO', weights=(9, 1))[0] for _ in range(cols)] for _ in range(rows)]
            with self.subTest(rows=rows, cols=cols, board=board):
                self.assertEqual(self.run_solve(board), expected_board(board))

    def test_constraint_sized_random(self):
        rng = random.Random(1302)
        board = [[rng.choice('XO') for _ in range(200)] for _ in range(200)]
        original = copy_board(board)
        self.assertEqual(self.run_solve(board), expected_board(original))

    def test_constraint_sized_all_open(self):
        board = [['O'] * 200 for _ in range(200)]
        result = self.run_solve(board)
        self.assertEqual(result, [['O'] * 200 for _ in range(200)])

    def test_constraint_sized_all_closed(self):
        board = [['X'] * 200 for _ in range(200)]
        self.assertEqual(self.run_solve(board), [['X'] * 200 for _ in range(200)])
        self.assertEqual(self.run_solve(board), expected_board([['X'] * 200 for _ in range(200)]))

    def test_constraint_sized_single_ring(self):
        # A 198 x 198 inner block, entirely surrounded by a one-cell ring of 'X',
        # is captured; the same block shifted to touch the border is not.
        board = [['X'] * 200 for _ in range(200)]
        for row in range(1, 199):
            for col in range(1, 199):
                board[row][col] = 'O'
        self.assertEqual(self.run_solve(board), [['X'] * 200 for _ in range(200)])

        touching = [['X'] * 200 for _ in range(200)]
        for row in range(0, 199):
            for col in range(0, 199):
                touching[row][col] = 'O'
        # The block touches the top and left borders, so it all survives; the
        # remaining last row and column of 'X' stay 'X'.
        self.assertEqual(self.run_solve(touching), touching)
        self.assertEqual(self.run_solve(touching), expected_board(touching))

    def test_constraint_sized_checkerboard(self):
        board = [['O' if (row + col) % 2 == 0 else 'X' for col in range(200)] for row in range(200)]
        expected = expected_board(board)
        self.assertEqual(self.run_solve(board), expected)
        # Only the border cells of the checkerboard survive, and every interior
        # 'O' is isolated by 'X' neighbours.
        survivors = sum(row.count('O') for row in expected)
        border_open = sum(
            1
            for row in range(200)
            for col in range(200)
            if (row + col) % 2 == 0 and (row in (0, 199) or col in (0, 199))
        )
        self.assertEqual(survivors, border_open)

    def test_constraint_sized_large_ring(self):
        # A ring of 'O' touching the border survives, and the interior stays 'X'.
        board = [['X'] * 200 for _ in range(200)]
        for index in range(200):
            board[0][index] = 'O'
            board[199][index] = 'O'
            board[index][0] = 'O'
            board[index][199] = 'O'
        self.assertEqual(self.run_solve(board), board)


if __name__ == '__main__':
    unittest.main()
