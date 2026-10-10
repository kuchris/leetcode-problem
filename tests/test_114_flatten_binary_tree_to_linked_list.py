"""Tests for 114. Flatten Binary Tree to Linked List.

The oracle deliberately does not flatten anything: it walks the *original* tree
with an explicit stack (the solution instead splices the left subtree in front of
the right one, recursively finding each predecessor) and records the pre-order
sequence of node objects and values. After flattening, the right spine must
reproduce exactly that sequence, node object by node object, which also proves
the mutation was in place and that no node was rebuilt or dropped.

The walk also asserts that every left pointer is None and bounds the number of
steps, so a cycle created by a wrong splice fails loudly instead of hanging.
"""

import itertools
import random
import unittest

from _loader import load_solution
from _trees import TreeNode, build, from_structure, serialize

Solution = load_solution('114-flatten-binary-tree-to-linked-list.py').Solution


def preorder_nodes(root) -> list:
    """Pre-order node objects, collected with an explicit stack."""
    ordered = []
    stack = [root] if root is not None else []
    while stack:
        node = stack.pop()
        ordered.append(node)
        if node.right is not None:
            stack.append(node.right)
        if node.left is not None:
            stack.append(node.left)
    return ordered


def all_shapes(size):
    if size == 0:
        yield None
        return
    for left_size in range(size):
        for left in all_shapes(left_size):
            for right in all_shapes(size - 1 - left_size):
                yield (left, right)


def fill(shape, values):
    iterator = iter(values)

    def place(node):
        if node is None:
            return None
        left, right = node
        return (next(iterator), place(left), place(right))

    if shape is None:
        return None
    return place(shape)


def chained(size: int, value: int = 0, side: str = 'right'):
    """Level-order list of a one-sided chain of `size` nodes."""
    if size <= 0:
        return []
    if side == 'right':
        # [v, null, v, null, ..., v]
        values = []
        for _ in range(size):
            values.extend([value, None])
        values.pop()
        return values
    # Left chain: [v, v, null, v, null, ..., v, null]
    values = [value]
    for _ in range(size - 1):
        values.extend([value, None])
    return values


class FlattenBinaryTreeToLinkedListTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().flatten

    def check(self, values):
        root = build(values)
        expected = preorder_nodes(root)
        self.assertIsNone(self.solve(root), 'flatten must modify in place')
        return self.verify(root, expected)

    def verify(self, root, expected_nodes):
        walked = []
        node = root
        while node is not None:
            self.assertLessEqual(len(walked), len(expected_nodes),
                                 'the flattened list contains a cycle')
            self.assertIsNone(node.left, 'a left pointer was not cleared')
            walked.append(node)
            node = node.right

        self.assertEqual(len(walked), len(expected_nodes), 'node count changed')
        self.assertEqual([n.val for n in walked], [n.val for n in expected_nodes])
        self.assertEqual(walked, expected_nodes,
                         'nodes were rebuilt or reordered instead of re-linked')
        return serialize(root)

    def test_official_examples(self):
        self.assertEqual(self.check([1, 2, 5, 3, 4, None, 6]),
                         [1, None, 2, None, 3, None, 4, None, 5, None, 6])
        self.assertEqual(self.check([]), [])
        self.assertEqual(self.check([0]), [0])

    def test_single_and_two_nodes(self):
        self.assertEqual(self.check([1]), [1])
        self.assertEqual(self.check([1, 2]), [1, None, 2])
        self.assertEqual(self.check([1, None, 2]), [1, None, 2])
        self.assertEqual(self.check([1, 2, 3]), [1, None, 2, None, 3])

    def test_shapes_with_known_preorder(self):
        # Left chain: pre-order is the level-order values top to bottom.
        root = TreeNode(1, TreeNode(2, TreeNode(3, TreeNode(4), None), None), None)
        expected = preorder_nodes(root)
        self.solve(root)
        self.verify(root, expected)
        self.assertEqual(serialize(root), [1, None, 2, None, 3, None, 4])

        # Already flat right chain is left alone.
        root = TreeNode(1, None, TreeNode(2, None, TreeNode(3)))
        expected = preorder_nodes(root)
        self.solve(root)
        self.verify(root, expected)
        self.assertEqual(serialize(root), [1, None, 2, None, 3])

        # Zig-zag.
        root = TreeNode(1, TreeNode(2, None, TreeNode(3, TreeNode(4), None)),
                        TreeNode(5, TreeNode(6), TreeNode(7)))
        expected = preorder_nodes(root)
        self.solve(root)
        self.verify(root, expected)
        self.assertEqual([n.val for n in preorder_nodes(root)], [1, 2, 3, 4, 5, 6, 7])

    def test_empty_tree(self):
        self.assertIsNone(self.solve(None))

    def test_duplicate_values_keep_node_identity(self):
        root = build([1, 1, 1, 1, 1, 1, 1])
        expected = preorder_nodes(root)
        self.solve(root)
        self.verify(root, expected)

    def test_exhaustive_small_shapes(self):
        for size in range(0, 6):
            for shape in all_shapes(size):
                for values in itertools.product((0, 1), repeat=size):
                    root = from_structure(fill(shape, values))
                    expected = preorder_nodes(root)
                    with self.subTest(size=size, values=values, shape=shape):
                        self.solve(root)
                        self.verify(root, expected)

    def test_random_trees(self):
        rng = random.Random(1140)
        for _ in range(300):
            size = rng.randint(0, 100)
            values = []
            if size:
                values.append(rng.randint(-100, 100))
                values.extend(
                    None if rng.random() < 0.3 else rng.randint(-100, 100)
                    for _ in range(size - 1)
                )
            root = build(values)
            expected = preorder_nodes(root)
            with self.subTest(size=size):
                self.solve(root)
                self.verify(root, expected)

    def test_constraint_sized(self):
        # 2000 nodes is the constraint maximum.
        for values in (chained(2000), chained(2000, side='left'),
                       list(range(2000)), [7] * 2000):
            root = build(values)
            expected = preorder_nodes(root)
            self.solve(root)
            self.verify(root, expected)

        # The shape that makes the predecessor search walk furthest: the root's
        # left subtree is a right chain of 1000 nodes and its right subtree is a
        # right chain of 999, so flattening has to walk the whole left chain.
        left_chain = None
        for value in range(1000, 0, -1):
            left_chain = TreeNode(value, None, left_chain)
        right_chain = None
        for value in range(1999, 1000, -1):
            right_chain = TreeNode(value, None, right_chain)
        caterpillar = TreeNode(0, left_chain, right_chain)
        expected = preorder_nodes(caterpillar)
        self.assertEqual(len(expected), 2000)
        self.solve(caterpillar)
        self.verify(caterpillar, expected)
        self.assertEqual([node.val for node in expected],
                         [0] + list(range(1, 1001)) + list(range(1001, 2000)))


if __name__ == '__main__':
    unittest.main()
