import itertools
import unittest

from _loader import load_solution

Solution = load_solution('27-remove-element.py').Solution


class RemoveElementTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().removeElement

    def check(self, nums, val, expected_kept):
        k = self.solve(nums, val)
        self.assertEqual(k, len(expected_kept))
        # The judge sorts the first k elements, so order is not required.
        self.assertEqual(sorted(nums[:k]), sorted(expected_kept))
        self.assertTrue(all(v != val for v in nums[:k]))
        return k

    def test_official_examples(self):
        self.check([3, 2, 2, 3], 3, [2, 2])
        self.check([0, 1, 2, 2, 3, 0, 4, 2], 2, [0, 0, 1, 3, 4])

    def test_empty_input(self):
        self.check([], 5, [])

    def test_every_element_removed(self):
        self.check([1, 1, 1], 1, [])

    def test_no_element_removed(self):
        self.check([1, 2, 3], 9, [1, 2, 3])

    def test_value_outside_element_range(self):
        self.check([0, 50], 100, [0, 50])

    def test_maximum_size(self):
        nums = [i % 2 for i in range(100)]
        self.check(nums, 1, [0] * 50)

    def test_exhaustive_small_cases(self):
        for size in range(6):
            for nums in itertools.product(range(3), repeat=size):
                for val in range(4):
                    with self.subTest(nums=nums, val=val):
                        self.check(
                            list(nums), val, [v for v in nums if v != val]
                        )


if __name__ == '__main__':
    unittest.main()
