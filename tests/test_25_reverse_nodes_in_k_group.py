import itertools
import unittest

from _lists import build, load_list_solution, to_list

module = load_list_solution('25-reverse-nodes-in-k-group.py')
Solution = module.Solution


def brute_force(values: list[int], k: int) -> list[int]:
    """Reverse each complete block of k, leaving a short tail alone."""
    result = []
    for start in range(0, len(values), k):
        block = values[start:start + k]
        result.extend(block[::-1] if len(block) == k else block)
    return result


class ReverseNodesInKGroupTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().reverseKGroup

    def reverse(self, values, k):
        return to_list(self.solve(build(values), k))

    def test_official_examples(self):
        self.assertEqual(self.reverse([1, 2, 3, 4, 5], 2), [2, 1, 4, 3, 5])
        self.assertEqual(self.reverse([1, 2, 3, 4, 5], 3), [3, 2, 1, 4, 5])

    def test_k_equals_one_is_identity(self):
        self.assertEqual(self.reverse([1, 2, 3], 1), [1, 2, 3])

    def test_k_equals_length_reverses_everything(self):
        self.assertEqual(self.reverse([1, 2, 3, 4], 4), [4, 3, 2, 1])

    def test_tail_shorter_than_k_is_untouched(self):
        self.assertEqual(self.reverse([1, 2, 3, 4, 5], 4), [4, 3, 2, 1, 5])

    def test_maximum_size(self):
        values = list(range(5000))
        for k in (1, 2, 3, 7, 2500, 4999, 5000):
            with self.subTest(k=k):
                self.assertEqual(self.reverse(values, k), brute_force(values, k))

    def test_exhaustive_small_cases(self):
        for size in range(1, 8):
            for values in itertools.product([0, 1], repeat=size):
                for k in range(1, size + 1):
                    with self.subTest(values=values, k=k):
                        self.assertEqual(
                            self.reverse(list(values), k),
                            brute_force(list(values), k),
                        )


if __name__ == '__main__':
    unittest.main()
