import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('42-trapping-rain-water.py').Solution


def brute_force(height: list[int]) -> int:
    """Per bar: min(tallest on the left, tallest on the right) - own height."""
    total = 0
    for i, h in enumerate(height):
        left = max(height[:i], default=0)
        right = max(height[i + 1:], default=0)
        total += max(0, min(left, right) - h)
    return total


def prefix_suffix(height: list[int]) -> int:
    """A second independent method using explicit prefix/suffix maxima."""
    n = len(height)
    if n == 0:
        return 0
    left = [0] * n
    right = [0] * n
    left[0] = height[0]
    for i in range(1, n):
        left[i] = max(left[i - 1], height[i])
    right[-1] = height[-1]
    for i in range(n - 2, -1, -1):
        right[i] = max(right[i + 1], height[i])
    return sum(min(left[i], right[i]) - height[i] for i in range(n))


class TrappingRainWaterTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().trap

    def test_official_examples(self):
        self.assertEqual(self.solve([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]), 6)
        self.assertEqual(self.solve([4, 2, 0, 3, 2, 5]), 9)

    def test_single_bar_traps_nothing(self):
        self.assertEqual(self.solve([5]), 0)

    def test_monotonic_inputs_trap_nothing(self):
        self.assertEqual(self.solve([1, 2, 3, 4, 5]), 0)
        self.assertEqual(self.solve([5, 4, 3, 2, 1]), 0)

    def test_flat_input_traps_nothing(self):
        self.assertEqual(self.solve([3] * 10), 0)

    def test_zero_heights_trap_nothing(self):
        self.assertEqual(self.solve([0, 0, 0]), 0)

    def test_valley_between_two_walls(self):
        self.assertEqual(self.solve([5, 0, 0, 0, 5]), 15)
        self.assertEqual(self.solve([2, 0, 2]), 2)

    def test_maximum_size(self):
        height = [100000] + [0] * 19998 + [100000]
        self.assertEqual(self.solve(height), 100000 * 19998)

    def test_exhaustive_small_cases(self):
        for size in range(1, 8):
            for height in itertools.product(range(4), repeat=size):
                with self.subTest(height=height):
                    expected = brute_force(list(height))
                    self.assertEqual(self.solve(list(height)), expected)
                    self.assertEqual(expected, prefix_suffix(list(height)))

    def test_randomised_larger_cases(self):
        rng = random.Random(42)
        for _ in range(50):
            height = [rng.randint(0, 100000) for _ in range(rng.randint(1, 200))]
            with self.subTest(length=len(height)):
                self.assertEqual(self.solve(list(height)), prefix_suffix(list(height)))


if __name__ == '__main__':
    unittest.main()
