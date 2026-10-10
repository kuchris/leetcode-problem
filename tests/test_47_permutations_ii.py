import itertools
import unittest

from _loader import load_solution

Solution = load_solution('47-permutations-ii.py').Solution


def brute_force(nums: list[int]) -> list[list[int]]:
    # Convert to lists so the comparison matches the solution's return type.
    return sorted(list(p) for p in set(itertools.permutations(nums)))


class PermutationsIITests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().permuteUnique

    def test_official_examples(self):
        self.assertEqual(
            sorted(self.solve([1, 1, 2])), sorted([[1, 1, 2], [1, 2, 1], [2, 1, 1]])
        )
        self.assertEqual(
            sorted(self.solve([1, 2, 3])),
            sorted([[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]),
        )

    def test_single_element(self):
        self.assertEqual(self.solve([1]), [[1]])

    def test_all_elements_identical(self):
        self.assertEqual(self.solve([2, 2, 2, 2]), [[2, 2, 2, 2]])

    def test_no_duplicates_returned(self):
        result = self.solve([1, 1, 1, 2, 2])
        self.assertEqual(len(result), len({tuple(p) for p in result}))

    def test_input_is_not_modified(self):
        nums = [2, 1, 1]
        self.solve(nums)
        self.assertEqual(sorted(nums), [1, 1, 2])

    def test_maximum_size(self):
        # 8 elements with 4 pairs of duplicates: 8! / 2^4 = 2520.
        result = self.solve([1, 1, 2, 2, 3, 3, 4, 4])
        self.assertEqual(len(result), 2520)
        self.assertEqual(len({tuple(p) for p in result}), 2520)

    def test_exhaustive_small_cases(self):
        for size in range(1, 7):
            for nums in itertools.combinations_with_replacement(range(3), size):
                with self.subTest(nums=nums):
                    self.assertEqual(
                        sorted(self.solve(list(nums))), brute_force(list(nums))
                    )


if __name__ == '__main__':
    unittest.main()
