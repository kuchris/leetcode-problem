import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('41-first-missing-positive.py').Solution


def brute_force(nums: list[int]) -> int:
    """Smallest positive integer absent from the set."""
    present = set(nums)
    candidate = 1
    while candidate in present:
        candidate += 1
    return candidate


class FirstMissingPositiveTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().firstMissingPositive

    def test_official_examples(self):
        self.assertEqual(self.solve([1, 2, 0]), 3)
        self.assertEqual(self.solve([3, 4, -1, 1]), 2)
        self.assertEqual(self.solve([7, 8, 9, 11, 12]), 1)

    def test_single_element(self):
        self.assertEqual(self.solve([1]), 2)
        self.assertEqual(self.solve([2]), 1)
        self.assertEqual(self.solve([0]), 1)
        self.assertEqual(self.solve([-1]), 1)

    def test_all_values_present_gives_n_plus_one(self):
        self.assertEqual(self.solve([1, 2, 3, 4, 5]), 6)

    def test_values_out_of_range_are_ignored(self):
        self.assertEqual(self.solve([2, 3, 4, 10 ** 9, -(10 ** 9)]), 1)

    def test_duplicates_do_not_break_the_swaps(self):
        self.assertEqual(self.solve([1, 1, 1, 2]), 3)
        self.assertEqual(self.solve([2, 2, 2]), 1)

    def test_maximum_size(self):
        nums = list(range(1, 100001))
        self.assertEqual(self.solve(nums), 100001)
        nums[50000] = -1
        self.assertEqual(self.solve(nums), 50001)

    def test_exhaustive_small_cases(self):
        for size in range(1, 7):
            for nums in itertools.product(range(-2, 5), repeat=size):
                with self.subTest(nums=nums):
                    self.assertEqual(self.solve(list(nums)), brute_force(list(nums)))

    def test_randomised_cases(self):
        rng = random.Random(41)
        for _ in range(100):
            nums = [rng.randint(-10, 30) for _ in range(rng.randint(1, 40))]
            with self.subTest(nums=nums):
                self.assertEqual(self.solve(list(nums)), brute_force(nums))


if __name__ == '__main__':
    unittest.main()
