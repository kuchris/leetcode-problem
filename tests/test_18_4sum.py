import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('18-4sum.py').Solution


def brute_force(nums: list[int], target: int) -> list[list[int]]:
    found = set()
    for quad in itertools.combinations(range(len(nums)), 4):
        values = [nums[i] for i in quad]
        if sum(values) == target:
            found.add(tuple(sorted(values)))
    return sorted(sorted(q) for q in found)


def normalise(quads: list[list[int]]) -> list[list[int]]:
    return sorted(sorted(q) for q in quads)


class FourSumTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().fourSum

    def test_official_examples(self):
        self.assertEqual(
            normalise(self.solve([1, 0, -1, 0, -2, 2], 0)),
            [[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]],
        )
        self.assertEqual(self.solve([2, 2, 2, 2, 2], 8), [[2, 2, 2, 2]])

    def test_too_short_input(self):
        self.assertEqual(self.solve([1, 2, 3], 6), [])

    def test_no_duplicate_quadruplets(self):
        result = self.solve([-2, -1, 0, 0, 1, 2, 2], 0)
        self.assertEqual(len(result), len({tuple(q) for q in result}))

    def test_large_values_and_target(self):
        big = 10 ** 9
        self.assertEqual(self.solve([big, big, big, big], 4 * big), [[big] * 4])
        self.assertEqual(self.solve([-big, -big, -big, -big], -4 * big), [[-big] * 4])

    def test_maximum_size(self):
        nums = [0] * 200
        self.assertEqual(self.solve(nums, 0), [[0, 0, 0, 0]])

    def test_exhaustive_small_cases(self):
        for size in range(1, 7):
            for nums in itertools.product(range(-2, 3), repeat=size):
                for target in range(-2, 3):
                    with self.subTest(nums=nums, target=target):
                        self.assertEqual(
                            normalise(self.solve(list(nums), target)),
                            brute_force(list(nums), target),
                        )

    def test_randomised_medium_cases(self):
        rng = random.Random(18)
        for _ in range(25):
            nums = [rng.randint(-15, 15) for _ in range(rng.randint(4, 30))]
            target = rng.randint(-10, 10)
            with self.subTest(nums=nums, target=target):
                self.assertEqual(
                    normalise(self.solve(list(nums), target)),
                    brute_force(list(nums), target),
                )


if __name__ == '__main__':
    unittest.main()
