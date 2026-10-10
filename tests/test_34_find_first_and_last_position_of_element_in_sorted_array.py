import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('34-find-first-and-last-position-of-element-in-sorted-array.py').Solution


def brute_force(nums: list[int], target: int) -> list[int]:
    indices = [i for i, value in enumerate(nums) if value == target]
    return [indices[0], indices[-1]] if indices else [-1, -1]


class FindFirstAndLastPositionTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().searchRange

    def test_official_examples(self):
        self.assertEqual(self.solve([5, 7, 7, 8, 8, 10], 8), [3, 4])
        self.assertEqual(self.solve([5, 7, 7, 8, 8, 10], 6), [-1, -1])
        self.assertEqual(self.solve([], 0), [-1, -1])

    def test_single_element(self):
        self.assertEqual(self.solve([1], 1), [0, 0])
        self.assertEqual(self.solve([1], 2), [-1, -1])

    def test_target_outside_the_range(self):
        self.assertEqual(self.solve([2, 3, 4], 1), [-1, -1])
        self.assertEqual(self.solve([2, 3, 4], 5), [-1, -1])

    def test_whole_array_is_the_target(self):
        self.assertEqual(self.solve([7] * 10, 7), [0, 9])

    def test_target_at_the_edges(self):
        self.assertEqual(self.solve([1, 1, 2, 2, 3], 1), [0, 1])
        self.assertEqual(self.solve([1, 1, 2, 2, 3], 3), [4, 4])

    def test_large_values(self):
        nums = [-(10 ** 9), -(10 ** 9), 10 ** 9]
        self.assertEqual(self.solve(nums, -(10 ** 9)), [0, 1])
        self.assertEqual(self.solve(nums, 10 ** 9), [2, 2])

    def test_maximum_size(self):
        nums = [value // 10 for value in range(100000)]
        for target in (0, 5000, 9999, 10000):
            with self.subTest(target=target):
                self.assertEqual(self.solve(nums, target), brute_force(nums, target))

    def test_exhaustive_small_cases(self):
        for size in range(6):
            for nums in itertools.combinations_with_replacement(range(3), size):
                for target in range(4):
                    with self.subTest(nums=nums, target=target):
                        self.assertEqual(
                            self.solve(list(nums), target), brute_force(list(nums), target)
                        )

    def test_randomised_cases(self):
        rng = random.Random(34)
        for _ in range(50):
            nums = sorted(rng.randint(-5, 5) for _ in range(rng.randint(0, 40)))
            target = rng.randint(-6, 6)
            with self.subTest(nums=nums, target=target):
                self.assertEqual(self.solve(list(nums), target), brute_force(nums, target))


if __name__ == '__main__':
    unittest.main()
