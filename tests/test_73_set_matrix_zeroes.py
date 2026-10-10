import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('73-set-matrix-zeroes.py').Solution


def brute_force(matrix: list[list[int]]) -> list[list[int]]:
    """Build a fresh matrix from the zero positions."""
    rows, columns = len(matrix), len(matrix[0])
    zero_rows = {i for i in range(rows) for j in range(columns) if matrix[i][j] == 0}
    zero_columns = {j for i in range(rows) for j in range(columns) if matrix[i][j] == 0}
    return [
        [0 if i in zero_rows or j in zero_columns else matrix[i][j] for j in range(columns)]
        for i in range(rows)
    ]


class SetMatrixZeroesTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().setZeroes

    def apply(self, matrix):
        work = [row[:] for row in matrix]
        self.solve(work)
        return work

    def test_official_examples(self):
        self.assertEqual(
            self.apply([[1, 1, 1], [1, 0, 1], [1, 1, 1]]),
            [[1, 0, 1], [0, 0, 0], [1, 0, 1]],
        )
        self.assertEqual(
            self.apply([[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]]),
            [[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]],
        )

    def test_no_zeroes_leaves_the_matrix_alone(self):
        matrix = [[1, 2], [3, 4]]
        self.assertEqual(self.apply(matrix), matrix)

    def test_single_cell(self):
        self.assertEqual(self.apply([[0]]), [[0]])
        self.assertEqual(self.apply([[5]]), [[5]])

    def test_first_row_and_column_are_handled(self):
        # A zero only in the first row must not clear the first column.
        self.assertEqual(self.apply([[0, 1], [1, 1]]), [[0, 0], [0, 1]])
        # A zero only in the first column must not clear the first row.
        self.assertEqual(self.apply([[1, 1], [0, 1]]), [[0, 1], [0, 0]])

    def test_returns_none_and_mutates_in_place(self):
        matrix = [[1, 0], [1, 1]]
        result = self.solve(matrix)
        self.assertIsNone(result)
        self.assertEqual(matrix, [[0, 0], [1, 0]])

    def test_maximum_size(self):
        matrix = [[1] * 200 for _ in range(200)]
        matrix[100][100] = 0
        self.assertEqual(self.apply(matrix), brute_force(matrix))

    def test_exhaustive_small_matrices(self):
        for rows in range(1, 4):
            for columns in range(1, 4):
                for cells in itertools.product([0, 1], repeat=rows * columns):
                    matrix = [list(cells[i * columns:(i + 1) * columns]) for i in range(rows)]
                    with self.subTest(matrix=matrix):
                        self.assertEqual(self.apply(matrix), brute_force(matrix))

    def test_randomised_matrices(self):
        rng = random.Random(73)
        for _ in range(200):
            rows, columns = rng.randint(1, 8), rng.randint(1, 8)
            matrix = [[rng.choice([0, 1, 2, 3]) for _ in range(columns)] for _ in range(rows)]
            with self.subTest(matrix=matrix):
                self.assertEqual(self.apply(matrix), brute_force(matrix))


if __name__ == '__main__':
    unittest.main()
