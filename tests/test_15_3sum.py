import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('15-3sum.py').Solution


def brute_force(nums: list[int]) -> list[list[int]]:
    """Check every index triple and deduplicate the results."""
    found = set()
    for triple in itertools.combinations(range(len(nums)), 3):
        values = [nums[i] for i in triple]
        if sum(values) == 0:
            found.add(tuple(sorted(values)))
    return sorted(sorted(t) for t in found)


def normalise(triplets: list[list[int]]) -> list[list[int]]:
    return sorted(sorted(t) for t in triplets)


class ThreeSumTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().threeSum

    def test_official_examples(self):
        self.assertEqual(
            normalise(self.solve([-1, 0, 1, 2, -1, -4])),
            [[-1, -1, 2], [-1, 0, 1]],
        )
        self.assertEqual(self.solve([0, 1, 1]), [])
        self.assertEqual(self.solve([0, 0, 0]), [[0, 0, 0]])

    def test_no_duplicate_triplets_are_returned(self):
        result = self.solve([-2, 0, 0, 2, 2])
        self.assertEqual(len(result), len({tuple(t) for t in result}))

    def test_all_zeros_reports_one_triplet_only(self):
        self.assertEqual(self.solve([0] * 10), [[0, 0, 0]])

    def test_large_values_do_not_overflow(self):
        self.assertEqual(
            normalise(self.solve([100000, -100000, 0])), [[-100000, 0, 100000]]
        )

    def test_maximum_size_without_a_solution(self):
        # Any triple of 1s and -1s sums to -3, -1, 1 or 3, never 0.
        nums = [1] * 1500 + [-1] * 1500
        self.assertEqual(self.solve(nums), [])

    def test_exhaustive_small_cases(self):
        for size in range(3, 7):
            for nums in itertools.product(range(-2, 3), repeat=size):
                with self.subTest(nums=nums):
                    self.assertEqual(
                        normalise(self.solve(list(nums))), brute_force(list(nums))
                    )

    def test_randomised_medium_cases(self):
        rng = random.Random(20261010)
        for _ in range(30):
            nums = [rng.randint(-20, 20) for _ in range(rng.randint(3, 40))]
            with self.subTest(nums=nums):
                self.assertEqual(
                    normalise(self.solve(list(nums))), brute_force(list(nums))
                )


if __name__ == '__main__':
    unittest.main()
