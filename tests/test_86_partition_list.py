"""Tests for 86. Partition List.

Oracle: a stable list partition, [v for v in values if v < x] + [v for v in
values if v >= x]. It never touches links, so it checks the ordering requirement
independently of the two-chain implementation under test.

The identity check (the returned chain must reuse the very nodes it was given)
is what distinguishes a real in-place repartition from a rebuild.
"""

import itertools
import random
import unittest

from _lists import build, load_list_solution, to_list

Solution = load_list_solution('86-partition-list.py').Solution


def brute_force(values: list[int], x: int) -> list[int]:
    return [v for v in values if v < x] + [v for v in values if v >= x]


class PartitionListTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().partition

    def partition(self, values, x):
        return to_list(self.solve(build(values), x))

    def test_official_examples(self):
        self.assertEqual(self.partition([1, 4, 3, 2, 5, 2], 3), [1, 2, 2, 4, 3, 5])
        self.assertEqual(self.partition([2, 1], 2), [1, 2])

    def test_empty_list(self):
        self.assertIsNone(self.solve(None, 3))
        self.assertEqual(self.partition([], 0), [])

    def test_single_node(self):
        self.assertEqual(self.partition([1], 3), [1])
        self.assertEqual(self.partition([5], 3), [5])
        self.assertEqual(self.partition([3], 3), [3])

    def test_every_node_below_x(self):
        self.assertEqual(self.partition([2, 1, 4, 3], 10), [2, 1, 4, 3])

    def test_every_node_at_or_above_x(self):
        self.assertEqual(self.partition([2, 4, 3], 0), [2, 4, 3])
        self.assertEqual(self.partition([2, 4, 3], 2), [2, 4, 3])

    def test_reordered_case_keeps_relative_order(self):
        values = [3, 1, 4, 1, 5, 9, 2, 6]
        self.assertEqual(self.partition(values, 4), [3, 1, 1, 2, 4, 5, 9, 6])

    def test_negative_values_and_boundary_x(self):
        values = [-100, -200, 100, 0, 200, -100]
        for x in (-200, -100, 0, 100, 200):
            with self.subTest(x=x):
                self.assertEqual(self.partition(values, x), brute_force(values, x))

    def test_duplicates_around_x(self):
        self.assertEqual(self.partition([2, 2, 2, 2], 2), [2, 2, 2, 2])
        self.assertEqual(self.partition([3, 3, 3, 3], 3), [3, 3, 3, 3])
        self.assertEqual(self.partition([1, 1, 3, 3], 2), [1, 1, 3, 3])
        self.assertEqual(self.partition([3, 1, 3, 1], 2), [1, 1, 3, 3])

    def test_values_are_split_and_none_are_lost(self):
        values = [5, 1, 5, 2, 5, 3]
        result = self.partition(values, 4)
        self.assertEqual(sorted(result), sorted(values))
        self.assertEqual(result, brute_force(values, 4))

    def test_nodes_are_reused_not_rebuilt(self):
        values = [1, 4, 3, 2, 5, 2]
        head = build(values)
        original = []
        node = head
        while node is not None:
            original.append(node)
            node = node.next

        result = self.solve(head, 3)
        walked = []
        node = result
        while node is not None and len(walked) <= len(original):
            walked.append(node)
            node = node.next
        self.assertIsNone(node, 'the result chain must not contain a cycle')
        self.assertEqual(len(walked), len(original))
        for node in walked:
            self.assertIn(node, original)

    def test_exhaustive_small_cases(self):
        for size in range(0, 6):
            for values in itertools.product(range(3), repeat=size):
                values = list(values)
                for x in (-1, 0, 1, 2, 3):
                    with self.subTest(values=values, x=x):
                        self.assertEqual(self.partition(values, x), brute_force(values, x))

    def test_randomised_cases(self):
        rng = random.Random(860)
        for _ in range(300):
            values = [rng.randint(-3, 3) for _ in range(rng.randint(0, 30))]
            x = rng.randint(-4, 4)
            with self.subTest(values=values, x=x):
                self.assertEqual(self.partition(values, x), brute_force(values, x))

    def test_constraint_sized(self):
        # 200 nodes is the constraint maximum, x at both ends of its range.
        rng = random.Random(861)
        values = [rng.randint(-100, 100) for _ in range(200)]
        for x in (-200, 0, 200):
            with self.subTest(x=x):
                self.assertEqual(self.partition(values, x), brute_force(values, x))

        # Every node strictly below the split: the second chain stays empty.
        values = list(range(-100, 100))
        self.assertEqual(self.partition(values, 200), values)
        self.assertEqual(self.partition(values, -200), values)

        # Strictly decreasing input forces every node to move.
        values = list(range(100, -100, -1))
        self.assertEqual(self.partition(values, 0), brute_force(values, 0))


if __name__ == '__main__':
    unittest.main()
