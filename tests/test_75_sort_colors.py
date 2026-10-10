import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('75-sort-colors.py').Solution


class SortColorsTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().sortColors

    def apply(self, nums):
        work = list(nums)
        self.solve(work)
        return work

    def test_official_examples(self):
        self.assertEqual(self.apply([2, 0, 2, 1, 1, 0]), [0, 0, 1, 1, 2, 2])
        self.assertEqual(self.apply([2, 0, 1]), [0, 1, 2])

    def test_single_element(self):
        for value in (0, 1, 2):
            with self.subTest(value=value):
                self.assertEqual(self.apply([value]), [value])

    def test_already_sorted(self):
        self.assertEqual(self.apply([0, 0, 1, 1, 2, 2]), [0, 0, 1, 1, 2, 2])

    def test_reverse_sorted(self):
        self.assertEqual(self.apply([2, 2, 1, 1, 0, 0]), [0, 0, 1, 1, 2, 2])

    def test_only_one_colour_present(self):
        self.assertEqual(self.apply([1] * 10), [1] * 10)
        self.assertEqual(self.apply([2] * 10), [2] * 10)
        self.assertEqual(self.apply([0] * 10), [0] * 10)

    def test_returns_none_and_mutates_in_place(self):
        nums = [2, 0, 1]
        result = self.solve(nums)
        self.assertIsNone(result)
        self.assertEqual(nums, [0, 1, 2])

    def test_maximum_size(self):
        rng = random.Random(75)
        nums = [rng.randint(0, 2) for _ in range(300)]
        self.assertEqual(self.apply(nums), sorted(nums))

    def test_exhaustive_small_cases(self):
        for size in range(1, 8):
            for nums in itertools.product(range(3), repeat=size):
                with self.subTest(nums=nums):
                    self.assertEqual(self.apply(nums), sorted(nums))

    def test_randomised_cases(self):
        rng = random.Random(750)
        for _ in range(200):
            nums = [rng.randint(0, 2) for _ in range(rng.randint(1, 60))]
            with self.subTest(length=len(nums)):
                self.assertEqual(self.apply(nums), sorted(nums))


if __name__ == '__main__':
    unittest.main()
