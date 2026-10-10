import itertools
import unittest

from _lists import build, load_list_solution, to_list

module = load_list_solution('24-swap-nodes-in-pairs.py')
Solution = module.Solution


def brute_force(values: list[int]) -> list[int]:
    """Swap each adjacent pair at the value level."""
    result = list(values)
    for i in range(0, len(result) - 1, 2):
        result[i], result[i + 1] = result[i + 1], result[i]
    return result


class SwapNodesInPairsTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().swapPairs

    def swap(self, values):
        return to_list(self.solve(build(values)))

    def test_official_examples(self):
        self.assertEqual(self.swap([1, 2, 3, 4]), [2, 1, 4, 3])
        self.assertEqual(self.swap([]), [])
        self.assertEqual(self.swap([1]), [1])
        self.assertEqual(self.swap([1, 2, 3]), [2, 1, 3])

    def test_maximum_size(self):
        values = list(range(100))
        self.assertEqual(self.swap(values), brute_force(values))

    def test_nodes_are_relinked_not_revalued(self):
        # The statement forbids changing values; a node's identity must survive.
        head = build([1, 2, 3, 4])
        first, second = head, head.next
        result = self.solve(head)
        self.assertIs(result, second)
        self.assertIs(result.next, first)

    def test_exhaustive_small_cases(self):
        for size in range(6):
            for values in itertools.product([0, 1, 2], repeat=size):
                with self.subTest(values=values):
                    self.assertEqual(
                        self.swap(list(values)), brute_force(list(values))
                    )


if __name__ == '__main__':
    unittest.main()
