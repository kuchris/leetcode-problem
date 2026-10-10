import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('16-3sum-closest.py').Solution


def best_distance(nums: list[int], target: int) -> int:
    """Smallest achievable |sum - target| over all index triples."""
    return min(
        abs(sum(nums[i] for i in triple) - target)
        for triple in itertools.combinations(range(len(nums)), 3)
    )


class ThreeSumClosestTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().threeSumClosest

    def test_official_examples(self):
        self.assertEqual(self.solve([-1, 2, 1, -4], 1), 2)
        self.assertEqual(self.solve([0, 0, 0], 1), 0)

    def test_exact_match_is_returned(self):
        self.assertEqual(self.solve([1, 2, 3], 6), 6)

    def test_minimum_length(self):
        self.assertEqual(self.solve([1, 2, 3], 100), 6)

    def test_maximum_size(self):
        nums = [1000] * 500
        self.assertEqual(self.solve(nums, 10000), 3000)

    def test_exhaustive_small_cases(self):
        for size in range(3, 6):
            for nums in itertools.product(range(-3, 4), repeat=size):
                for target in range(-4, 5):
                    with self.subTest(nums=nums, target=target):
                        result = self.solve(list(nums), target)
                        # Ties are possible, so compare the achieved distance.
                        self.assertEqual(
                            abs(result - target), best_distance(list(nums), target)
                        )

    def test_randomised_medium_cases(self):
        rng = random.Random(16)
        for _ in range(40):
            nums = [rng.randint(-1000, 1000) for _ in range(rng.randint(3, 30))]
            target = rng.randint(-10000, 10000)
            with self.subTest(nums=nums, target=target):
                result = self.solve(list(nums), target)
                self.assertEqual(
                    abs(result - target), best_distance(list(nums), target)
                )


if __name__ == '__main__':
    unittest.main()
