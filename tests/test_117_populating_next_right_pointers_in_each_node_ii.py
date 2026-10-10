"""Tests for 117. Populating Next Right Pointers in Each Node II.

Oracles:
  - ``link_levels`` (``_next_nodes``): the problem statement transcribed — a
    plain level-order BFS groups the nodes by depth and chains each group. It
    spends O(n) memory on a queue, so it shares nothing with the constant-space
    pointer walk under test.
  - ``link_errors``: identity-compares every ``next`` pointer against that BFS
    grouping. Unlike a serialized output it catches a link that points at the
    right value in the wrong level, and it pins the "last node of a level keeps
    next = None" rule.
  - ``serialize``: reads each level by following ``next`` and emits the ``'#'``
    terminated format of the statement, used for the official examples.

Exhaustive sweep: every binary tree shape with up to six nodes, with distinct
values so the expected output is exact. The 6000-node cases (the constraint
maximum) cover a complete tree, both chains, and a sparse random tree.
"""

import itertools
import random
import unittest

from _next_nodes import Node, build, levels, link_levels, serialize, to_values
from _next_nodes import load_next_tree_solution

Solution = load_next_tree_solution(
    '117-populating-next-right-pointers-in-each-node-ii.py',
).Solution


def all_shapes(size):
    """Every binary tree shape with `size` nodes, as nested (left, right) pairs."""
    if size == 0:
        yield None
        return
    for left_size in range(size):
        for left in all_shapes(left_size):
            for right in all_shapes(size - 1 - left_size):
                yield (left, right)


def tree_from_shape(shape, counter=None) -> "Node | None":
    """Materialise a shape with distinct pre-order values (1, 2, 3, ...)."""
    if counter is None:
        counter = itertools.count(1)
    if shape is None:
        return None
    left, right = shape
    # Arguments evaluate left to right, so numbering is pre-order.
    return Node(next(counter), tree_from_shape(left, counter), tree_from_shape(right, counter))


def link_errors(root) -> list:
    """Every ``next`` pointer that disagrees with the BFS level grouping."""
    problems = []
    for depth, group in enumerate(levels(root)):
        for node, target in zip(group, group[1:] + [None]):
            if node.next is not target:
                problems.append((
                    depth,
                    node.val,
                    None if node.next is None else node.next.val,
                ))
    return problems


def random_tree(rng, size) -> "Node | None":
    """A random tree holding exactly `size` nodes.

    Each new node is attached to a uniformly chosen free child slot, so the
    result is a genuine random shape with holes - never a value list that
    ``build`` would truncate because its first slots are null.
    """
    if size <= 0:
        return None
    root = Node(rng.randint(-100, 100))
    nodes = [root]
    free = [root]
    while len(nodes) < size:
        node = free[rng.randrange(len(free))]
        if node.left is None and node.right is None:
            side = 'left' if rng.random() < 0.5 else 'right'
        elif node.left is None:
            side = 'left'
        else:
            side = 'right'
        child = Node(rng.randint(-100, 100))
        setattr(node, side, child)
        if node.left is not None and node.right is not None:
            free.remove(node)
        free.append(child)
        nodes.append(child)
    return root


class PopulatingNextRightPointersTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().connect

    def check(self, values):
        """Run the solution and the BFS oracle on two copies of the same tree."""
        actual = build(values)
        expected = build(values)
        result = self.solve(actual)
        link_levels(expected)
        self.assertIs(result, actual)
        self.assertEqual(link_errors(actual), [])
        self.assertEqual(serialize(actual), serialize(expected))
        return actual

    def test_official_examples(self):
        root = self.check([1, 2, 3, 4, 5, None, 7])
        self.assertEqual(serialize(root), [1, '#', 2, 3, '#', 4, 5, 7, '#'])

        empty = self.solve(build([]))
        self.assertIsNone(empty)
        self.assertEqual(serialize(empty), [])

    def test_empty_and_single_node(self):
        self.check([])
        root = self.check([42])
        self.assertIsNone(root.next)

    def test_last_node_of_each_level_keeps_next_none(self):
        root = self.check([1, 2, 3, 4, None, None, 5])
        for group in levels(root):
            self.assertIsNone(group[-1].next)

    def test_chains(self):
        # A right chain: one node per level, so every next must stay None.
        root = self.check([1, None, 2, None, 3, None, 4])
        self.assertEqual(
            [[node.val for node in group] for group in levels(root)],
            [[1], [2], [3], [4]],
        )
        self.assertEqual(serialize(root), [1, '#', 2, '#', 3, '#', 4, '#'])

        # A left chain with the same shape mirrored.
        root = self.check([1, 2, None, 3, None, 4])
        self.assertEqual(serialize(root), [1, '#', 2, '#', 3, '#', 4, '#'])

    def test_levels_with_holes(self):
        # 5's next neighbour skips the missing slot to reach 7.
        self.check([1, 2, 3, 4, 5, None, 7])
        # A node whose only child is on the right, and one whose only child is
        # on the left, on adjacent levels.
        self.check([1, 2, None, None, 3, 4, 5, 6, None, None, 7])
        # Children of a node that is not the first of its level still chain.
        self.check([1, 2, 3, None, 4, None, 5, 6, 7, None, 8])

    def test_exhaustive_shapes_up_to_six_nodes(self):
        for size in range(0, 7):
            for shape in all_shapes(size):
                with self.subTest(size=size, shape=shape):
                    actual = tree_from_shape(shape)
                    expected = tree_from_shape(shape)
                    self.solve(actual)
                    link_levels(expected)
                    self.assertEqual(link_errors(actual), [])
                    self.assertEqual(serialize(actual), serialize(expected))

    def test_random_level_order_trees(self):
        rng = random.Random(1170)
        for _ in range(400):
            size = rng.randint(0, 90)
            values = to_values(random_tree(rng, size))
            with self.subTest(values=values[:12]):
                self.check(values)

    def test_constraint_sized(self):
        # A complete tree with the maximum 6000 nodes.
        complete = list(range(1, 6001))
        root = self.check(complete)
        self.assertEqual(sum(len(group) for group in levels(root)), 6000)

        # A 6000-node right chain: every level holds exactly one node.
        chain = []
        for value in range(1, 6001):
            chain.append(value)
            chain.append(None)
        chain.pop()
        root = self.check(chain)
        self.assertEqual(sum(len(group) for group in levels(root)), 6000)
        self.assertTrue(all(len(group) == 1 for group in levels(root)))

        # The mirrored left chain.
        left_chain = [1]
        for value in range(2, 6001):
            left_chain.append(value)
            left_chain.append(None)
        root = self.check(left_chain)
        self.assertEqual(sum(len(group) for group in levels(root)), 6000)

        # A sparse random tree, where many levels start with a deep subtree.
        rng = random.Random(1171)
        root = random_tree(rng, 6000)
        self.assertEqual(sum(len(group) for group in levels(root)), 6000)
        self.check(to_values(root))


if __name__ == '__main__':
    unittest.main()
