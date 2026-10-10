"""Tests for 148. Sort List.

Oracles:
  - ``sorted()``: Timsort over the extracted values.
  - ``list_merge_sort``: a recursive top-down merge sort written against plain
    Python lists — a different decomposition (top-down halves) from the
    bottom-up, in-place pointer merges under test.
  - node identity: the sorted chain must reuse the input node objects. Each
    case compares the multiset of ``id()``s, and ``walk`` rejects cycles and
    repeated nodes, so rebuilding the nodes or dropping the tail is caught.

Exhaustive sweep: every sequence of length 0..5 over {0, 1, 2} plus every
permutation of four and five values. Constraint-sized cases use 50000 nodes in
the shapes that stress run detection: sorted, reversed, all equal, two-valued
and random.
"""

import itertools
import random
import time
import unittest

from _lists import build, load_list_solution, to_list

Solution = load_list_solution('148-sort-list.py').Solution

MAX_NODES = 50_000
MAX_VALUE = 10 ** 5


def list_merge_sort(values) -> list:
    """Recursive top-down merge sort on a Python list."""
    if len(values) <= 1:
        return list(values)
    middle = len(values) // 2
    left = list_merge_sort(values[:middle])
    right = list_merge_sort(values[middle:])
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def walk(head) -> list:
    """The nodes of a chain; fails loudly on a cycle or a repeated node."""
    nodes = []
    seen = set()
    node = head
    while node is not None:
        node_id = id(node)
        if node_id in seen:
            raise AssertionError('the result chain revisits a node')
        seen.add(node_id)
        nodes.append(node)
        node = node.next
        if len(nodes) > 2 * MAX_NODES + 10:
            raise AssertionError('the result chain does not terminate')
    return nodes


class SortListTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().sortList

    def check(self, values):
        """Sort a fresh chain and verify values *and* node identity."""
        original = build(values)
        original_ids = sorted(id(node) for node in walk(original))
        result = self.solve(original)
        result_nodes = walk(result)
        self.assertEqual([node.val for node in result_nodes], sorted(values))
        self.assertEqual([node.val for node in result_nodes], list_merge_sort(values))
        self.assertEqual(sorted(id(node) for node in result_nodes), original_ids)
        return result_nodes

    def test_official_examples(self):
        self.assertEqual(to_list(self.solve(build([4, 2, 1, 3]))), [1, 2, 3, 4])
        self.assertEqual(to_list(self.solve(build([-1, 5, 3, 4, 0]))), [-1, 0, 3, 4, 5])
        self.assertIsNone(self.solve(build([])))
        self.check([4, 2, 1, 3])
        self.check([-1, 5, 3, 4, 0])
        self.check([])

    def test_single_node_and_pair(self):
        nodes = self.check([7])
        self.assertEqual(len(nodes), 1)
        self.assertIsNone(nodes[0].next)
        self.check([2, 1])
        self.check([1, 2])
        self.check([2, 2])

    def test_duplicates_are_kept(self):
        self.check([3, 1, 3, 1, 3])
        self.check([0, 0, -1, -1, 5, 5])
        self.check([MAX_VALUE, -MAX_VALUE, 0, MAX_VALUE, -MAX_VALUE])

    def test_result_reuses_the_input_nodes(self):
        head = build([3, 1, 2])
        by_value = {}
        for node in walk(head):
            by_value[node.val] = node
        result_nodes = self.solve(head)
        self.assertIs(result_nodes, by_value[1])
        self.assertIs(result_nodes.next, by_value[2])
        self.assertIs(result_nodes.next.next, by_value[3])
        self.assertIsNone(result_nodes.next.next.next)

    def test_exhaustive_small_sequences(self):
        for length in range(0, 6):
            for values in itertools.product((0, 1, 2), repeat=length):
                values = list(values)
                with self.subTest(values=values):
                    self.check(values)
        for values in itertools.permutations((0, 1, 2, 5)):
            with self.subTest(values=values):
                self.check(list(values))
        for values in itertools.permutations((0, 1, 2, 5, 9)):
            with self.subTest(values=values):
                self.check(list(values))

    def test_random_sequences(self):
        rng = random.Random(1480)
        for _ in range(300):
            length = rng.randint(0, 40)
            values = [rng.randint(-6, 6) for _ in range(length)]
            with self.subTest(values=values[:8]):
                self.check(values)

    def test_constraint_sized_shapes(self):
        # Already sorted and reversed: Timsort-style run handling is not
        # available to a pure merge sort, so both shapes are checked.
        self.check(list(range(1, MAX_NODES + 1)))
        self.check(list(range(MAX_NODES, 0, -1)))
        # All equal, and only two distinct values.
        self.check([0] * MAX_NODES)
        self.check([0, MAX_VALUE] * (MAX_NODES // 2))
        # Values at both extremes of the allowed range.
        extremes = [MAX_VALUE if index % 3 else -MAX_VALUE for index in range(MAX_NODES)]
        self.check(extremes)
        # Random order over the full range.
        rng = random.Random(1481)
        self.check([rng.randint(-MAX_VALUE, MAX_VALUE) for _ in range(MAX_NODES)])

    def test_constraint_sized_runtime(self):
        # A rough, generous budget so a quadratic implementation would fail.
        rng = random.Random(1482)
        values = [rng.randint(-MAX_VALUE, MAX_VALUE) for _ in range(MAX_NODES)]
        head = build(values)
        start = time.perf_counter()
        result = self.solve(head)
        elapsed = time.perf_counter() - start
        self.assertEqual([node.val for node in walk(result)], sorted(values))
        self.assertLess(elapsed, 10.0, f'n={MAX_NODES} took {elapsed:.2f}s')


if __name__ == '__main__':
    unittest.main()
