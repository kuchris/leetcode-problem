import itertools
import unittest

from _loader import load_solution

Solution = load_solution('11-container-with-most-water.py').Solution


def brute_force(height: list[int]) -> int:
    """Try every pair of lines."""
    best = 0
    for i in range(len(height)):
        for j in range(i + 1, len(height)):
            best = max(best, min(height[i], height[j]) * (j - i))
    return best


class ContainerWithMostWaterTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().maxArea

    def test_official_examples(self):
        self.assertEqual(self.solve([1, 8, 6, 2, 5, 4, 8, 3, 7]), 49)
        self.assertEqual(self.solve([1, 1]), 1)

    def test_minimum_length(self):
        self.assertEqual(self.solve([0, 0]), 0)
        self.assertEqual(self.solve([4, 3]), 3)

    def test_zero_heights_give_zero(self):
        self.assertEqual(self.solve([0, 0, 0, 0]), 0)

    def test_maximum_size(self):
        height = [10000] * 100000
        self.assertEqual(self.solve(height), 10000 * 99999)

    def test_exhaustive_small_cases(self):
        for size in range(2, 6):
            for height in itertools.product(range(4), repeat=size):
                with self.subTest(height=height):
                    self.assertEqual(self.solve(list(height)), brute_force(list(height)))


if __name__ == '__main__':
    unittest.main()
