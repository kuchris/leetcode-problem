"""Tests for 147. Insertion Sort List.

Oracles:
  - ``sorted()``: Timsort over the extracted values, an entirely different
    algorithm from insertion sort on a linked list.
  - ``list_insertion_sort``: the textbook array insertion sort — the same
    definition (grow a sorted prefix, insert the next element in place) written
    against a Python list, so it pins the specification independently of any
    pointer handling.
  - node identity: the result must be built from the *same* node objects. Every
    case compares the multiset of ``id()``s of the input nodes with the output
    nodes, so an implementation that copies values into fresh nodes fails even
    though its values are right. ``walk`` also rejects cycles and repeats.

Exhaustive sweep: every sequence of length 1..5 over {0, 1, 2} and every
permutation of four values. Constraint-sized cases use 5000 nodes, including an
order built to maximise insertion scans.
"""

import itertools
import random
import time
import unittest

from _lists import build, load_list_solution, to_list

Solution = load_list_solution('147-insertion-sort-list.py').Solution

MAX_NODES = 5000
MAX_VALUE = 5000


def list_insertion_sort(values) -> list:
    """Array insertion sort: the problem's definition on a Python list."""
    result = []
    for value in values:
        position = len(result)
        while position > 0 and result[position - 1] > value:
            position -= 1
        result.insert(position, value)
    return result


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


def worst_case_values(size) -> list:
    """An order that forces a scan of about half the sorted run per insertion.

    A single large value keeps the tail large (so the append fast path never
    triggers), then values expand outward around the middle of the range: each
    new value has to walk past everything smaller than it.
    """
    half = size // 2
    values = [MAX_VALUE]
    for step in range(half):
        values.append(half - step)
        values.append(half + step)
    return values[:size]


class InsertionSortListTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().insertionSortList

    def check(self, values):
        """Sort a fresh chain and verify values *and* node identity."""
        original = build(values)
        original_ids = sorted(id(node) for node in walk(original))
        result = self.solve(original)
        result_nodes = walk(result)
        self.assertEqual([node.val for node in result_nodes], sorted(values))
        self.assertEqual([node.val for node in result_nodes], list_insertion_sort(values))
        self.assertEqual(sorted(id(node) for node in result_nodes), original_ids)
        return result_nodes

    def test_official_examples(self):
        self.assertEqual(to_list(self.solve(build([4, 2, 1, 3]))), [1, 2, 3, 4])
        self.assertEqual(to_list(self.solve(build([-1, 5, 3, 4, 0]))), [-1, 0, 3, 4, 5])
        self.check([4, 2, 1, 3])
        self.check([-1, 5, 3, 4, 0])

    def test_single_node(self):
        nodes = self.check([7])
        self.assertEqual(len(nodes), 1)
        self.assertIsNone(nodes[0].next)

    def test_already_sorted_and_reverse_sorted(self):
        self.check([1, 2, 3, 4, 5])
        self.check([5, 4, 3, 2, 1])
        self.check([2, 2, 2, 2])

    def test_duplicates_are_kept(self):
        self.check([3, 1, 3, 1, 3])
        self.check([0, 0, -1, -1, 5, 5])
        self.check([MAX_VALUE, -MAX_VALUE, 0, MAX_VALUE])

    def test_result_reuses_the_input_nodes(self):
        head = build([3, 1, 2])
        # Keep a handle on each original node before the relink.
        by_value = {}
        for node in walk(head):
            by_value[node.val] = node
        result_nodes = self.solve(head)
        self.assertIs(result_nodes, by_value[1])
        self.assertIs(result_nodes.next, by_value[2])
        self.assertIs(result_nodes.next.next, by_value[3])
        self.assertIsNone(result_nodes.next.next.next)

    def test_exhaustive_small_sequences(self):
        for length in range(1, 6):
            for values in itertools.product((0, 1, 2), repeat=length):
                values = list(values)
                with self.subTest(values=values):
                    self.check(values)
        for values in itertools.permutations((0, 1, 2, 5)):
            with self.subTest(values=values):
                self.check(list(values))

    def test_random_sequences(self):
        rng = random.Random(1470)
        for _ in range(300):
            length = rng.randint(1, 30)
            values = [rng.randint(-5, 5) for _ in range(length)]
            with self.subTest(values=values[:8]):
                self.check(values)

    def test_constraint_sized_shapes(self):
        # Already sorted: the append fast path makes this linear.
        self.check(list(range(1, MAX_NODES + 1)))
        # Reverse sorted: every insertion lands at the front.
        self.check(list(range(MAX_NODES, 0, -1)))
        # All equal values.
        self.check([0] * MAX_NODES)
        # The adversarial middle-insertion order.
        self.check(worst_case_values(MAX_NODES))
        # Random order over the full value range.
        rng = random.Random(1471)
        self.check([rng.randint(-MAX_VALUE, MAX_VALUE) for _ in range(MAX_NODES)])

    def test_constraint_sized_worst_case_runtime(self):
        values = worst_case_values(MAX_NODES)
        self.assertEqual(len(values), MAX_NODES)
        self.assertTrue(all(-MAX_VALUE <= value <= MAX_VALUE for value in values))
        head = build(values)
        start = time.perf_counter()
        result = self.solve(head)
        elapsed = time.perf_counter() - start
        self.assertEqual([node.val for node in walk(result)], sorted(values))
        self.assertLess(elapsed, 10.0, f'worst case took {elapsed:.2f}s at n={MAX_NODES}')


if __name__ == '__main__':
    unittest.main()
