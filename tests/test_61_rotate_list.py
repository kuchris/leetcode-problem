import itertools
import unittest

from _lists import build, load_list_solution, to_list

module = load_list_solution('61-rotate-list.py')
Solution = module.Solution


def brute_force(values: list[int], k: int) -> list[int]:
    """Rotate the values with list slicing."""
    if not values:
        return []
    k %= len(values)
    if k == 0:
        return list(values)
    return values[-k:] + values[:-k]


class RotateListTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().rotateRight

    def rotate(self, values, k):
        return to_list(self.solve(build(values), k))

    def test_official_examples(self):
        self.assertEqual(self.rotate([1, 2, 3, 4, 5], 2), [4, 5, 1, 2, 3])
        self.assertEqual(self.rotate([0, 1, 2], 4), [2, 0, 1])

    def test_empty_and_single_node(self):
        self.assertEqual(self.rotate([], 0), [])
        self.assertEqual(self.rotate([], 5), [])
        self.assertEqual(self.rotate([7], 0), [7])
        self.assertEqual(self.rotate([7], 100), [7])

    def test_k_zero_is_identity(self):
        self.assertEqual(self.rotate([1, 2, 3], 0), [1, 2, 3])

    def test_k_equal_to_length_is_identity(self):
        self.assertEqual(self.rotate([1, 2, 3], 3), [1, 2, 3])
        self.assertEqual(self.rotate([1, 2, 3], 6), [1, 2, 3])

    def test_maximum_k(self):
        values = list(range(10))
        self.assertEqual(self.rotate(values, 2 * 10 ** 9), brute_force(values, 2 * 10 ** 9))

    def test_maximum_size(self):
        values = list(range(500))
        for k in (0, 1, 250, 499, 500, 501, 2 * 10 ** 9):
            with self.subTest(k=k):
                self.assertEqual(self.rotate(values, k), brute_force(values, k))

    def test_exhaustive_small_cases(self):
        for size in range(6):
            for values in itertools.product([0, 1, 2], repeat=size):
                for k in range(0, 8):
                    with self.subTest(values=values, k=k):
                        self.assertEqual(
                            self.rotate(list(values), k), brute_force(list(values), k)
                        )


if __name__ == '__main__':
    unittest.main()
