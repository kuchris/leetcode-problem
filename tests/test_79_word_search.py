"""Tests for 79. Word Search.

Oracle: enumerate every ordered tuple of distinct cells with itertools and keep
the first whose letters spell the word and whose consecutive cells are adjacent.
That checks the definition directly, with no DFS and no board mutation.
"""

import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('79-word-search.py').Solution


def brute_force(board: list[list[str]], word: str) -> bool:
    """Every self-avoiding path of len(word) cells against the word."""
    rows, cols = len(board), len(board[0])
    cells = [(r, c) for r in range(rows) for c in range(cols)]
    if len(word) > len(cells):
        return False
    for path in itertools.permutations(cells, len(word)):
        if any(board[r][c] != ch for (r, c), ch in zip(path, word)):
            continue
        if all(
            abs(path[i][0] - path[i + 1][0]) + abs(path[i][1] - path[i + 1][1]) == 1
            for i in range(len(path) - 1)
        ):
            return True
    return False


OFFICIAL_BOARD = [['A', 'B', 'C', 'E'],
                  ['S', 'F', 'C', 'S'],
                  ['A', 'D', 'E', 'E']]

SHAPES = [(1, 1), (1, 2), (2, 2), (2, 3)]


class WordSearchTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().exist

    def test_official_examples(self):
        self.assertTrue(self.solve([row[:] for row in OFFICIAL_BOARD], 'ABCCED'))
        self.assertTrue(self.solve([row[:] for row in OFFICIAL_BOARD], 'SEE'))
        self.assertFalse(self.solve([row[:] for row in OFFICIAL_BOARD], 'ABCB'))

    def test_single_cell_board(self):
        self.assertTrue(self.solve([['a']], 'a'))
        self.assertFalse(self.solve([['a']], 'b'))
        self.assertFalse(self.solve([['a']], 'aa'))

    def test_word_longer_than_the_board(self):
        self.assertFalse(self.solve([['a']], 'aa'))
        self.assertFalse(self.solve([['a', 'b']], 'abab'))
        self.assertFalse(self.solve([['a', 'b'], ['c', 'd']], 'abcde'))

    def test_a_cell_cannot_be_used_twice(self):
        self.assertFalse(self.solve([['a']], 'aa'))
        self.assertTrue(self.solve([['a', 'a']], 'aa'))
        # Three distinct cells, so this path is legal.
        self.assertTrue(self.solve([['a', 'b', 'a']], 'aba'))
        # These would only succeed if a cell could be revisited (or if a cell
        # could be skipped): a -> b -> a needs three cells, and the board has two.
        self.assertFalse(self.solve([['a', 'b']], 'aba'))
        self.assertFalse(self.solve([['a', 'a']], 'aaa'))

    def test_single_letter_words(self):
        self.assertTrue(self.solve([['x']], 'x'))
        self.assertTrue(self.solve([['a', 'b'], ['c', 'd']], 'd'))
        self.assertFalse(self.solve([['a', 'b'], ['c', 'd']], 'z'))

    def test_board_is_restored_after_searching(self):
        board = [['A', 'B'], ['C', 'D']]
        snapshot = [row[:] for row in board]
        self.assertTrue(self.solve(board, 'AB'))
        self.assertEqual(board, snapshot)
        board = [['A', 'B'], ['C', 'D']]
        snapshot = [row[:] for row in board]
        self.assertFalse(self.solve(board, 'ZZ'))
        self.assertEqual(board, snapshot)

    def test_exhaustive_small_cases(self):
        letters = 'AB'
        for rows, cols in SHAPES:
            for flat in itertools.product(letters, repeat=rows * cols):
                board = [list(flat[r * cols:(r + 1) * cols]) for r in range(rows)]
                for length in range(1, 4):
                    for word_letters in itertools.product(letters, repeat=length):
                        word = ''.join(word_letters)
                        with self.subTest(board=board, word=word):
                            self.assertEqual(
                                self.solve([row[:] for row in board], word),
                                brute_force(board, word),
                            )

    def test_randomised_cases(self):
        rng = random.Random(790)
        for _ in range(60):
            rows, cols = rng.choice([(2, 2), (2, 3), (3, 3)])
            board = [[rng.choice('ABC') for _ in range(cols)] for _ in range(rows)]
            length = rng.randint(1, 4)
            if rng.random() < 0.5:
                # Walk a real self-avoiding path so True answers occur too.
                r, c = rng.randrange(rows), rng.randrange(cols)
                used = {(r, c)}
                word = board[r][c]
                for _ in range(length - 1):
                    options = [(r + dr, c + dc) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))
                               if 0 <= r + dr < rows and 0 <= c + dc < cols
                               and (r + dr, c + dc) not in used]
                    if not options:
                        break
                    r, c = rng.choice(options)
                    used.add((r, c))
                    word += board[r][c]
            else:
                word = ''.join(rng.choice('ABC') for _ in range(length))
            with self.subTest(board=board, word=word):
                self.assertEqual(
                    self.solve([row[:] for row in board], word),
                    brute_force(board, word),
                )

    def test_constraint_sized(self):
        # 6 x 6 board, 15-letter word: the largest shape the constraints allow.
        all_a = [['A'] * 6 for _ in range(6)]
        self.assertTrue(self.solve([row[:] for row in all_a], 'A' * 15))
        self.assertFalse(self.solve([row[:] for row in all_a], 'B' * 15))
        self.assertFalse(self.solve([row[:] for row in all_a], 'A' * 14 + 'B'))

        # A planted snake spells the only possible 15-letter word on the board.
        word = 'ABCDEFGHIJKLMNO'
        snake = ([(0, c) for c in range(6)]
                 + [(1, 5 - c) for c in range(6)]
                 + [(2, 0), (2, 1), (2, 2)])
        board = [['X'] * 6 for _ in range(6)]
        for (r, c), ch in zip(snake, word):
            board[r][c] = ch
        self.assertTrue(self.solve([row[:] for row in board], word))
        self.assertFalse(self.solve([row[:] for row in board], word + 'P'))

        # A 15-letter word confined to a 12-cell region cannot exist.
        blocks = [['A'] * 6, ['A'] * 6] + [['B'] * 6 for _ in range(4)]
        self.assertFalse(self.solve([row[:] for row in blocks], 'A' * 13))
        self.assertTrue(self.solve([row[:] for row in blocks], 'A' * 12))


if __name__ == '__main__':
    unittest.main()
