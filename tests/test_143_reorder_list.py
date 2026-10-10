"""Tests for 143. Reorder List.

Oracle: the required order is computed from the *values* alone by walking two
indices from the outside in -- L0, Ln, L1, Ln-1, ... -- which has nothing to do
with linked-list surgery, so it cannot inherit a bug from the solution's
middle-find / reverse / merge passes.

Identity is checked separately, because "you may not modify the values in the
nodes, only the nodes themselves":
  - the multiset of (id(node), value) pairs must be preserved (no node rebuilt,
    no value moved between nodes, none lost);
  - for a list with distinct values the walked node objects must be exactly the
    nodes that held those values before the call;
  - the chain must still have exactly n nodes (a wrong splice would create a
    cycle, which the bounded walk detects).
"""

import itertools
import random
import unittest

from _lists import build, load_list_solution

Solution = load_list_solution('143-reorder-list.py').Solution


def expected_order(values) -> list:
    """L0, Ln, L1, Ln-1, ... computed from the values alone."""
    out = []
    low, high = 0, len(values) - 1
    while low <= high:
        out.append(values[low])
        low += 1
        if low <= high:
            out.append(values[high])
            high -= 1
    return out


def walk_bounded(head, limit: int):
    """Walk at most `limit` nodes; returns (nodes, extra) where extra is the node
    after the limit (non-None means the chain is longer than the original)."""
    nodes = []
    node = head
    while node is not None and len(nodes) < limit:
        nodes.append(node)
        node = node.next
    return nodes, node


class ReorderListTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().reorderList

    def check(self, values):
        head = build(values)
        original, overflow = walk_bounded(head, len(values) + 1)
        self.assertIsNone(overflow)
        self.assertEqual([node.val for node in original], list(values))
        pairs_before = {(id(node), node.val) for node in original}
        distinct = len(set(values)) == len(values)
        node_of_value = {node.val: node for node in original} if distinct else {}

        self.assertIsNone(self.solve(head), 'reorderList must modify in place')

        after, overflow = walk_bounded(head, len(values))
        self.assertIsNone(overflow, 'the reordered chain has more nodes than before')
        self.assertEqual(len(after), len(values))
        self.assertEqual([node.val for node in after], expected_order(values))
        self.assertEqual({(id(node), node.val) for node in after}, pairs_before)
        if distinct:
            self.assertEqual(after, [node_of_value[value]
                                     for value in expected_order(values)])
        return [node.val for node in after]

    def test_official_examples(self):
        self.assertEqual(self.check([1, 2, 3, 4]), [1, 4, 2, 3])
        self.assertEqual(self.check([1, 2, 3, 4, 5]), [1, 5, 2, 4, 3])

    def test_small_sizes(self):
        self.assertEqual(self.check([1]), [1])
        self.assertEqual(self.check([1, 2]), [1, 2])
        self.assertEqual(self.check([1, 2, 3]), [1, 3, 2])
        self.assertEqual(self.check([1, 2, 3, 4, 5, 6]), [1, 6, 2, 5, 3, 4])

    def test_boundary_values(self):
        self.assertEqual(self.check([1000]), [1000])
        self.assertEqual(self.check([1, 1000]), [1, 1000])
        self.assertEqual(self.check([1000] * 5), [1000] * 5)

    def test_duplicate_values(self):
        self.assertEqual(self.check([1, 1, 1, 1]), [1, 1, 1, 1])
        self.assertEqual(self.check([1, 2, 1, 2]), [1, 2, 2, 1])
        self.assertEqual(self.check([1, 1, 2, 2]), [1, 2, 1, 2])

    def test_exhaustive_distinct_values(self):
        for size in range(1, 9):
            values = list(range(1, size + 1))
            with self.subTest(size=size):
                self.check(values)

    def test_exhaustive_duplicate_values(self):
        for size in range(1, 8):
            for values in itertools.product((1, 2), repeat=size):
                with self.subTest(size=size, values=values):
                    self.check(list(values))

    def test_random_cases(self):
        rng = random.Random(1430)
        for _ in range(200):
            size = rng.randint(1, 500)
            values = [rng.randint(1, 1000) for _ in range(size)]
            with self.subTest(size=size):
                self.check(values)
        for _ in range(50):
            size = rng.randint(1, 500)
            values = rng.sample(range(1, 1001), size)
            with self.subTest(size=size, distinct=True):
                self.check(values)

    def test_constraint_sized(self):
        # 5 * 10^4 nodes is the constraint maximum, values in [1, 1000].
        size = 50_000
        rng = random.Random(1431)
        values = [rng.randint(1, 1000) for _ in range(size)]
        produced = self.check(values)
        self.assertEqual(produced, expected_order(values))

        # The maximum size with distinct values (values are bounded by 1000).
        values = list(range(1, 1001))
        self.check(values)

        # A sorted and a reverse-sorted maximum-size list.
        self.check(list(range(1, 1001)))
        self.check(list(range(1000, 0, -1)))


if __name__ == '__main__':
    unittest.main()
