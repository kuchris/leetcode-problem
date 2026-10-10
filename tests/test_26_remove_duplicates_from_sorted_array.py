import itertools
import unittest

from _loader import load_solution

Solution = load_solution('26-remove-duplicates-from-sorted-array.py').Solution


class RemoveDuplicatesTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().removeDuplicates

    def check(self, nums, expected_unique):
        k = self.solve(nums)
        self.assertEqual(k, len(expected_unique))
        self.assertEqual(nums[:k], expected_unique)
        return k

    def test_official_examples(self):
        self.check([1, 1, 2], [1, 2])
        self.check([0, 0, 1, 1, 1, 2, 2, 3, 3, 4], [0, 1, 2, 3, 4])

    def test_single_element(self):
        self.check([5], [5])

    def test_all_identical(self):
        self.check([7] * 10, [7])

    def test_already_unique(self):
        self.check([-100, 0, 50, 100], [-100, 0, 50, 100])

    def test_negative_values(self):
        self.check([-3, -3, -1, -1, -1, 0], [-3, -1, 0])

    def test_maximum_size(self):
        nums = [i // 3 for i in range(30000)]
        self.check(nums, sorted(set(nums)))

    def test_exhaustive_small_cases(self):
        for size in range(1, 8):
            for nums in itertools.combinations_with_replacement(range(-2, 3), size):
                with self.subTest(nums=nums):
                    self.check(list(nums), sorted(set(nums)))


if __name__ == '__main__':
    unittest.main()
