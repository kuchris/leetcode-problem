import itertools
import unittest

from _loader import load_solution

Solution = load_solution('31-next-permutation.py').Solution


def brute_force(nums: list[int]) -> list[int]:
    """List the distinct permutations in order and take the following one."""
    ordered = sorted({p for p in itertools.permutations(nums)})
    current = tuple(nums)
    index = ordered.index(current)
    return list(ordered[(index + 1) % len(ordered)])


class NextPermutationTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().nextPermutation

    def apply(self, nums):
        self.solve(nums)
        return nums

    def test_official_examples(self):
        self.assertEqual(self.apply([1, 2, 3]), [1, 3, 2])
        self.assertEqual(self.apply([3, 2, 1]), [1, 2, 3])
        self.assertEqual(self.apply([1, 1, 5]), [1, 5, 1])

    def test_single_element_is_unchanged(self):
        self.assertEqual(self.apply([7]), [7])

    def test_all_elements_equal(self):
        self.assertEqual(self.apply([2, 2, 2, 2]), [2, 2, 2, 2])

    def test_last_permutation_wraps_to_the_first(self):
        self.assertEqual(self.apply([4, 3, 2, 1]), [1, 2, 3, 4])

    def test_returns_none_and_mutates_in_place(self):
        nums = [1, 3, 2]
        result = self.solve(nums)
        self.assertIsNone(result)
        self.assertEqual(nums, [2, 1, 3])

    def test_exhaustive_small_cases(self):
        for size in range(1, 6):
            for nums in itertools.product(range(3), repeat=size):
                with self.subTest(nums=nums):
                    self.assertEqual(
                        self.apply(list(nums)), brute_force(list(nums))
                    )

    def test_cycles_through_every_permutation(self):
        nums = [1, 2, 3, 4]
        seen = []
        for _ in range(24):
            seen.append(tuple(nums))
            self.solve(nums)
        self.assertEqual(len(set(seen)), 24)
        self.assertEqual(sorted(seen), sorted(itertools.permutations([1, 2, 3, 4])))


if __name__ == '__main__':
    unittest.main()
