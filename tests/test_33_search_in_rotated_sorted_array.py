import unittest

from _loader import load_solution

Solution = load_solution('33-search-in-rotated-sorted-array.py').Solution


class SearchInRotatedSortedArrayTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().search

    def test_official_examples(self):
        self.assertEqual(self.solve([4, 5, 6, 7, 0, 1, 2], 0), 4)
        self.assertEqual(self.solve([4, 5, 6, 7, 0, 1, 2], 3), -1)
        self.assertEqual(self.solve([1], 0), -1)

    def test_single_element(self):
        self.assertEqual(self.solve([1], 1), 0)
        self.assertEqual(self.solve([5], 4), -1)

    def test_not_rotated(self):
        nums = [1, 2, 3, 4, 5]
        for index, value in enumerate(nums):
            with self.subTest(target=value):
                self.assertEqual(self.solve(nums, value), index)

    def test_rotated_by_one(self):
        self.assertEqual(self.solve([5, 1, 2, 3, 4], 5), 0)
        self.assertEqual(self.solve([5, 1, 2, 3, 4], 4), 4)

    def test_negative_values(self):
        self.assertEqual(self.solve([-1, 0, 1, 2, -5, -4], -5), 4)

    def test_maximum_size(self):
        nums = list(range(1, 5001))
        for rotation in (0, 1, 2500, 4999):
            rotated = nums[rotation:] + nums[:rotation]
            for target in (1, 2500, 5000):
                with self.subTest(rotation=rotation, target=target):
                    self.assertEqual(self.solve(rotated, target), rotated.index(target))

    def test_exhaustive_rotations_and_targets(self):
        base = [0, 1, 2, 3, 4, 5]
        for rotation in range(len(base)):
            rotated = base[rotation:] + base[:rotation]
            for target in range(-2, 8):
                with self.subTest(rotation=rotation, target=target):
                    expected = rotated.index(target) if target in rotated else -1
                    self.assertEqual(self.solve(rotated, target), expected)


if __name__ == '__main__':
    unittest.main()
