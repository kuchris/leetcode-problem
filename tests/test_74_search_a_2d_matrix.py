import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('74-search-a-2d-matrix.py').Solution


def brute_force(matrix: list[list[int]], target: int) -> bool:
    return any(target in row for row in matrix)


def build_sorted_matrix(rows: int, columns: int, values) -> list[list[int]]:
    """Lay a sorted sequence out row by row, which satisfies both guarantees."""
    flat = sorted(values)
    return [flat[i * columns:(i + 1) * columns] for i in range(rows)]


class SearchA2DMatrixTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().searchMatrix

    def test_official_examples(self):
        matrix = [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]]
        self.assertTrue(self.solve(matrix, 3))
        self.assertFalse(self.solve(matrix, 13))

    def test_single_cell(self):
        self.assertTrue(self.solve([[1]], 1))
        self.assertFalse(self.solve([[1]], 0))

    def test_single_row_and_column(self):
        self.assertTrue(self.solve([[1, 2, 3, 4]], 3))
        self.assertFalse(self.solve([[1, 2, 3, 4]], 5))
        self.assertTrue(self.solve([[1], [2], [3]], 3))
        self.assertFalse(self.solve([[1], [2], [3]], 0))

    def test_boundary_values(self):
        matrix = [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]]
        self.assertTrue(self.solve(matrix, 1))
        self.assertTrue(self.solve(matrix, 60))
        self.assertFalse(self.solve(matrix, 0))
        self.assertFalse(self.solve(matrix, 61))
        self.assertFalse(self.solve(matrix, 8))

    def test_negative_values(self):
        matrix = [[-10, -5], [-1, 0], [3, 9]]
        for target in (-10, -5, -1, 0, 3, 9):
            with self.subTest(target=target):
                self.assertTrue(self.solve(matrix, target))
        self.assertFalse(self.solve(matrix, -6))

    def test_maximum_size(self):
        matrix = build_sorted_matrix(100, 100, range(10000))
        for target in (0, 4999, 9999, 10000, -1):
            with self.subTest(target=target):
                self.assertEqual(self.solve(matrix, target), brute_force(matrix, target))

    def test_exhaustive_small_matrices(self):
        for rows in range(1, 4):
            for columns in range(1, 4):
                for values in itertools.combinations_with_replacement(range(-2, 4), rows * columns):
                    matrix = build_sorted_matrix(rows, columns, values)
                    for target in range(-3, 6):
                        with self.subTest(matrix=matrix, target=target):
                            self.assertEqual(
                                self.solve(matrix, target), brute_force(matrix, target)
                            )

    def test_randomised_matrices(self):
        rng = random.Random(74)
        for _ in range(200):
            rows, columns = rng.randint(1, 8), rng.randint(1, 8)
            matrix = build_sorted_matrix(
                rows, columns, [rng.randint(-20, 20) for _ in range(rows * columns)]
            )
            for target in (rng.randint(-25, 25) for _ in range(4)):
                with self.subTest(matrix=matrix, target=target):
                    self.assertEqual(self.solve(matrix, target), brute_force(matrix, target))


if __name__ == '__main__':
    unittest.main()
