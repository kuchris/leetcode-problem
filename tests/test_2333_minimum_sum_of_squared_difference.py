import importlib.util
import itertools
from functools import cache
from pathlib import Path
import unittest


source = Path(__file__).resolve().parents[1] / 'solutions' / '2333-minimum-sum-of-squared-difference.py'
spec = importlib.util.spec_from_file_location('solution_2333', source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@cache
def brute_force(differences: tuple[int, ...], budget: int) -> int:
    """Try every possible next reduction, independently of binary search."""
    if budget == 0 or not any(differences):
        return sum(d * d for d in differences)
    return min(
        brute_force(differences[:i] + (d - 1,) + differences[i + 1:], budget - 1)
        for i, d in enumerate(differences)
        if d > 0
    )


class MinimumSquaredDifferenceTests(unittest.TestCase):
    def setUp(self):
        self.solve = module.Solution().minSumSquareDiff

    def test_official_examples(self):
        self.assertEqual(self.solve([1, 2, 3, 4], [2, 10, 20, 19], 0, 0), 579)
        self.assertEqual(self.solve([1, 4, 10, 12], [5, 8, 6, 9], 1, 1), 43)

    def test_zero_and_excess_budget(self):
        self.assertEqual(self.solve([5], [5], 0, 0), 0)
        self.assertEqual(self.solve([0], [100000], 100000, 0), 0)
        self.assertEqual(self.solve([0], [1], 10**9, 10**9), 0)

    def test_leftover_operations_and_inputs_unchanged(self):
        nums1, nums2 = [0, 10, 0], [5, 5, 5]
        self.assertEqual(self.solve(nums1, nums2, 1, 1), 57)
        self.assertEqual(nums1, [0, 10, 0])
        self.assertEqual(nums2, [5, 5, 5])

    def test_exhaustive_small_cases(self):
        for size in range(1, 5):
            for differences in itertools.product(range(4), repeat=size):
                for budget in range(sum(differences) + 2):
                    with self.subTest(differences=differences, budget=budget):
                        self.assertEqual(
                            self.solve(list(differences), [0] * size, budget // 2, budget - budget // 2),
                            brute_force(differences, budget),
                        )

    def test_maximum_size_and_large_integer_result(self):
        size, difference, budget = 100000, 100000, 1999999999
        reduction, remainder = divmod(budget, size)
        cap = difference - reduction
        expected = (size - remainder) * cap**2 + remainder * (cap - 1)**2
        self.assertEqual(
            self.solve([0] * size, [difference] * size, 10**9, budget - 10**9),
            expected,
        )


if __name__ == '__main__':
    unittest.main()
