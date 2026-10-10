"""Tests for 82. Remove Duplicates from Sorted List II.

Oracle: count the values as plain Python data and keep the ones whose count is
exactly one. Because the input is guaranteed sorted ascending, sorting the
distinct values reproduces the required output order without touching any
linked list.
"""

import itertools
import random
import unittest
from collections import Counter

from _lists import build, load_list_solution, to_list

Solution = load_list_solution('82-remove-duplicates-from-sorted-list-ii.py').Solution


def brute_force(values: list[int]) -> list[int]:
    """Keep only the values that occur exactly once, in sorted order."""
    counts = Counter(values)
    return [value for value in sorted(counts) if counts[value] == 1]


class RemoveDuplicatesFromSortedListIITests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().deleteDuplicates

    def delete(self, values):
        return to_list(self.solve(build(values)))

    def test_official_examples(self):
        self.assertEqual(self.delete([1, 2, 3, 3, 4, 4, 5]), [1, 2, 5])
        self.assertEqual(self.delete([1, 1, 1, 2, 3]), [2, 3])

    def test_empty_list(self):
        self.assertIsNone(self.solve(None))
        self.assertEqual(self.delete([]), [])

    def test_single_node(self):
        self.assertEqual(self.delete([1]), [1])
        self.assertEqual(self.delete([-100]), [-100])
        self.assertEqual(self.delete([100]), [100])

    def test_two_nodes(self):
        self.assertEqual(self.delete([1, 1]), [])
        self.assertEqual(self.delete([1, 2]), [1, 2])

    def test_every_node_is_a_duplicate(self):
        self.assertEqual(self.delete([5, 5, 5, 5]), [])
        self.assertEqual(self.delete([1, 1, 2, 2, 3, 3]), [])

    def test_no_duplicates_at_all(self):
        self.assertEqual(self.delete([1, 2, 3, 4]), [1, 2, 3, 4])

    def test_runs_at_both_ends(self):
        self.assertEqual(self.delete([1, 1, 2, 3, 3]), [2])
        self.assertEqual(self.delete([1, 1, 2, 2, 3]), [3])
        self.assertEqual(self.delete([1, 2, 2, 3, 3]), [1])

    def test_boundary_values(self):
        values = [-100, -100, -100, -99, 99, 100, 100]
        self.assertEqual(self.delete(values), [-99, 99])

    def test_result_is_sorted_and_free_of_duplicates(self):
        values = [1, 1, 2, 3, 3, 3, 4, 5, 5, 6]
        result = self.delete(values)
        self.assertEqual(result, sorted(result))
        self.assertEqual(len(set(result)), len(result))

    def test_exhaustive_small_cases(self):
        for size in range(0, 7):
            for values in itertools.combinations_with_replacement(range(-1, 2), size):
                values = list(values)
                with self.subTest(values=values):
                    self.assertEqual(self.delete(values), brute_force(values))

    def test_randomised_cases(self):
        rng = random.Random(820)
        for _ in range(300):
            values = sorted(rng.randint(-5, 5) for _ in range(rng.randint(0, 40)))
            with self.subTest(values=values):
                self.assertEqual(self.delete(values), brute_force(values))

    def test_constraint_sized(self):
        # 300 nodes is the constraint maximum.
        rng = random.Random(821)
        values = []
        value = -100
        while len(values) < 300:
            values.extend([value] * rng.randint(1, 4))
            value += 1
        values = sorted(values[:300])
        self.assertEqual(len(values), 300)
        self.assertGreaterEqual(values[0], -100)
        self.assertLessEqual(values[-1], 100)
        self.assertEqual(self.delete(values), brute_force(values))

        self.assertEqual(self.delete([-100] * 150 + [100] * 150), [])
        self.assertEqual(self.delete(list(range(-100, 100))), list(range(-100, 100)))


if __name__ == '__main__':
    unittest.main()
