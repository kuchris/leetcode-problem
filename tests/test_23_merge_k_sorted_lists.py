import itertools
import unittest

from _lists import build, load_list_solution, to_list

module = load_list_solution('23-merge-k-sorted-lists.py')
Solution = module.Solution


class MergeKSortedListsTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().mergeKLists

    def merge(self, groups):
        return to_list(self.solve([build(group) for group in groups]))

    def test_official_examples(self):
        self.assertEqual(
            self.merge([[1, 4, 5], [1, 3, 4], [2, 6]]),
            [1, 1, 2, 3, 4, 4, 5, 6],
        )
        self.assertEqual(self.merge([]), [])
        self.assertEqual(self.merge([[]]), [])

    def test_empty_lists_are_ignored(self):
        self.assertEqual(self.merge([[], [1], [], [0, 2], []]), [0, 1, 2])

    def test_single_list_is_unchanged(self):
        self.assertEqual(self.merge([[1, 2, 3]]), [1, 2, 3])

    def test_duplicate_values_across_lists(self):
        # Equal heads must not force comparisons between ListNode objects.
        self.assertEqual(self.merge([[1, 1], [1, 1], [1]]), [1, 1, 1, 1, 1])

    def test_negative_values(self):
        self.assertEqual(self.merge([[-10000, 0], [-5, 10000]]), [-10000, -5, 0, 10000])

    def test_maximum_total_nodes(self):
        groups = [[i] for i in range(10000)]
        self.assertEqual(self.merge(groups), list(range(10000)))

    def test_exhaustive_small_cases(self):
        pool = [0, 1, 2]
        candidates = [[]]
        for size in range(1, 4):
            candidates += [list(c) for c in itertools.combinations_with_replacement(pool, size)]
        for k in range(4):
            for groups in itertools.product(candidates, repeat=k):
                with self.subTest(groups=groups):
                    expected = sorted(v for group in groups for v in group)
                    self.assertEqual(self.merge([list(g) for g in groups]), expected)


if __name__ == '__main__':
    unittest.main()
