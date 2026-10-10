"""Tests for 84. Largest Rectangle in Histogram.

Oracle: try every span [i, j] and use its minimum bar, O(n^2). That is the
definition of the answer, with no stack and no notion of "previous smaller bar".
"""

import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('84-largest-rectangle-in-histogram.py').Solution


def brute_force(heights: list[int]) -> int:
    """Best rectangle over all spans, using the span's shortest bar."""
    best = 0
    for i in range(len(heights)):
        lowest = heights[i]
        for j in range(i, len(heights)):
            if heights[j] < lowest:
                lowest = heights[j]
            area = lowest * (j - i + 1)
            if area > best:
                best = area
    return best


def increasing_answer(n: int) -> int:
    """Answer for heights 1..n, from the closed form for a sorted histogram."""
    return max((i + 1) * (n - i) for i in range(n))


class LargestRectangleInHistogramTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().largestRectangleArea

    def test_official_examples(self):
        self.assertEqual(self.solve([2, 1, 5, 6, 2, 3]), 10)
        self.assertEqual(self.solve([2, 4]), 4)

    def test_single_bar(self):
        self.assertEqual(self.solve([0]), 0)
        self.assertEqual(self.solve([1]), 1)
        self.assertEqual(self.solve([10 ** 4]), 10 ** 4)

    def test_all_zero(self):
        self.assertEqual(self.solve([0] * 50), 0)

    def test_all_equal(self):
        for height in (1, 3, 10 ** 4):
            with self.subTest(height=height):
                self.assertEqual(self.solve([height] * 20), height * 20)

    def test_sorted_histograms(self):
        for n in (1, 2, 5, 40):
            heights = list(range(1, n + 1))
            with self.subTest(n=n):
                self.assertEqual(self.solve(heights), increasing_answer(n))
                self.assertEqual(self.solve(heights[::-1]), increasing_answer(n))

    def test_single_tall_bar_between_zeros(self):
        self.assertEqual(self.solve([0, 0, 5, 0, 0]), 5)
        self.assertEqual(self.solve([2, 0, 2, 0, 2]), 2)

    def test_wide_low_rectangle_beats_tall_narrow_pair(self):
        # Two tall bars are worth 8, the one-unit valley spans all four bars.
        self.assertEqual(self.solve([4, 1, 4, 1]), 4)
        self.assertEqual(self.solve([1, 1, 1, 100]), 100)
        self.assertEqual(self.solve([2, 2, 2, 100, 2]), 100)

    def test_exhaustive_small_cases(self):
        for size in range(1, 7):
            for heights in itertools.product(range(4), repeat=size):
                heights = list(heights)
                with self.subTest(heights=heights):
                    self.assertEqual(self.solve(heights), brute_force(heights))

    def test_randomised_cases(self):
        rng = random.Random(840)
        for _ in range(200):
            heights = [rng.randint(0, 12) for _ in range(rng.randint(1, 60))]
            with self.subTest(heights=heights):
                self.assertEqual(self.solve(heights), brute_force(heights))

    def test_randomised_small_alphabet(self):
        # Many equal neighbours exercise the >= comparison in the stack pop.
        rng = random.Random(841)
        for _ in range(200):
            heights = [rng.choice([1, 1, 1, 2, 5]) for _ in range(rng.randint(1, 40))]
            with self.subTest(heights=heights):
                self.assertEqual(self.solve(heights), brute_force(heights))

    def test_medium_case_against_oracle(self):
        rng = random.Random(842)
        heights = [rng.randint(0, 10 ** 4) for _ in range(600)]
        self.assertEqual(self.solve(heights), brute_force(heights))

        heights = sorted(rng.randint(0, 10 ** 4) for _ in range(600))
        self.assertEqual(self.solve(heights), brute_force(heights))

    def test_constraint_sized(self):
        n = 10 ** 5

        self.assertEqual(self.solve([10 ** 4] * n), 10 ** 4 * n)
        self.assertEqual(self.solve([0] * n), 0)

        heights = list(range(1, n + 1))
        expected = increasing_answer(n)
        self.assertEqual(self.solve(heights), expected)
        self.assertEqual(self.solve(heights[::-1]), expected)

        # One tall spike in an otherwise empty histogram.
        spike = [0] * n
        spike[n // 2] = 10 ** 4
        self.assertEqual(self.solve(spike), 10 ** 4)

        # A tall block in the middle: 3 * 1000 * 10000.
        block = [0] * n
        for i in range(n // 2, n // 2 + 1000):
            block[i] = 10 ** 4
        self.assertEqual(self.solve(block), 1000 * 10 ** 4)


if __name__ == '__main__':
    unittest.main()
