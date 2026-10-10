import itertools
import unittest

from _loader import load_solution

Solution = load_solution('46-permutations.py').Solution


class PermutationsTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().permute

    def test_official_examples(self):
        self.assertEqual(
            sorted(self.solve([1, 2, 3])),
            sorted([[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]),
        )
        self.assertEqual(sorted(self.solve([0, 1])), sorted([[0, 1], [1, 0]]))
        self.assertEqual(self.solve([1]), [[1]])

    def test_result_count_is_n_factorial(self):
        for size in range(1, 7):
            with self.subTest(size=size):
                result = self.solve(list(range(size)))
                self.assertEqual(len(result), len(list(itertools.permutations(range(size)))))

    def test_negative_values(self):
        self.assertEqual(sorted(self.solve([-10, 10])), sorted([[-10, 10], [10, -10]]))

    def test_no_duplicate_permutations(self):
        result = self.solve([1, 2, 3, 4])
        self.assertEqual(len(result), len({tuple(p) for p in result}))

    def test_input_is_not_modified(self):
        nums = [1, 2, 3]
        self.solve(nums)
        self.assertEqual(nums, [1, 2, 3])

    def test_maximum_size(self):
        result = self.solve([1, 2, 3, 4, 5, 6])
        self.assertEqual(len(result), 720)
        self.assertEqual(sorted(result), sorted([list(p) for p in itertools.permutations([1, 2, 3, 4, 5, 6])]))

    def test_exhaustive_small_cases(self):
        for size in range(1, 6):
            for nums in itertools.combinations(range(-2, 4), size):
                with self.subTest(nums=nums):
                    self.assertEqual(
                        sorted(self.solve(list(nums))),
                        sorted([list(p) for p in itertools.permutations(nums)]),
                    )


if __name__ == '__main__':
    unittest.main()
