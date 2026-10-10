"""Tests for 110. Balanced Binary Tree.

Oracle: the definition written literally -- for every node, compute the heights
of its two subtrees with a recursive height function and require the difference
to be at most one, then recurse into both children. It is O(n^2) and it does not
reuse the bottom-up idea the solution is built on, so it is an independent
authority on small and medium trees.

For the 5000-node constraint cases the quadratic oracle is the wrong tool, so
they are decided from the definition as well but cheaply: the root's child
heights are measured with an iterative height walk, and a perfect tree is
checked node by node with an iterative bottom-up balance checker.
"""

import random
import sys
import unittest

from _loader import load_solution
from _trees import TreeNode, build

Solution = load_solution('110-balanced-binary-tree.py').Solution

# The literal oracle recurses as deep as the tree, and the constraint allows a
# 5000-node chain.
sys.setrecursionlimit(20000)


def height(node) -> int:
    if node is None:
        return 0
    return 1 + max(height(node.left), height(node.right))


def literal_oracle(node) -> bool:
    if node is None:
        return True
    if abs(height(node.left) - height(node.right)) > 1:
        return False
    return literal_oracle(node.left) and literal_oracle(node.right)


def iterative_heights(root) -> dict:
    """id(node) -> height, bottom-up, without early exit."""
    table = {}
    if root is None:
        return table
    stack = [(root, False)]
    while stack:
        node, expanded = stack.pop()
        if not expanded:
            stack.append((node, True))
            if node.right is not None:
                stack.append((node.right, False))
            if node.left is not None:
                stack.append((node.left, False))
            continue
        left = table[id(node.left)] if node.left is not None else 0
        right = table[id(node.right)] if node.right is not None else 0
        table[id(node)] = 1 + max(left, right)
    return table


def balance_of_root_children(root) -> int:
    """|height(left) - height(right)| at the root, or 0 for a missing root."""
    if root is None:
        return 0
    table = iterative_heights(root)
    left = table[id(root.left)] if root.left is not None else 0
    right = table[id(root.right)] if root.right is not None else 0
    return abs(left - right)


def all_shapes(size):
    if size == 0:
        yield None
        return
    for left_size in range(size):
        for left in all_shapes(left_size):
            for right in all_shapes(size - 1 - left_size):
                yield (left, right)


def shape_tree(shape, value=0):
    """Turn a shape into a tree whose values are irrelevant to the answer."""
    if shape is None:
        return None
    left, right = shape
    return TreeNode(value, shape_tree(left, value), shape_tree(right, value))


def chain(size: int, value=0) -> "TreeNode | None":
    """A right-leaning chain of `size` nodes."""
    root = None
    for _ in range(size):
        root = TreeNode(value, None, root)
    return root


def perfect(height_: int, value=0) -> "TreeNode | None":
    if height_ == 0:
        return None
    return TreeNode(value, perfect(height_ - 1, value), perfect(height_ - 1, value))


class BalancedBinaryTreeTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().isBalanced

    def check(self, values):
        root = build(values)
        self.assertEqual(self.solve(root), literal_oracle(root))
        return root

    def test_official_examples(self):
        self.assertTrue(self.solve(build([3, 9, 20, None, None, 15, 7])))
        self.assertFalse(self.solve(build([1, 2, 2, 3, 3, None, None, 4, 4])))
        self.assertTrue(self.solve(build([])))
        self.assertTrue(self.solve(None))

    def test_small_shapes(self):
        self.assertTrue(self.solve(TreeNode(0)))
        self.assertTrue(self.solve(TreeNode(0, TreeNode(0), None)))
        self.assertFalse(self.solve(TreeNode(0, TreeNode(0, TreeNode(0), None), None)))
        self.assertTrue(self.solve(TreeNode(0, TreeNode(0), TreeNode(0))))
        # Balanced at the root but unbalanced deeper down.
        deep = TreeNode(0, TreeNode(0, TreeNode(0, TreeNode(0), None), None), TreeNode(0))
        self.assertFalse(self.solve(deep))

    def test_exhaustive_shapes_up_to_seven_nodes(self):
        for size in range(0, 8):
            for shape in all_shapes(size):
                root = shape_tree(shape)
                with self.subTest(size=size, shape=shape):
                    self.assertEqual(self.solve(root), literal_oracle(root))

    def test_random_level_order_trees(self):
        rng = random.Random(1100)
        for _ in range(400):
            size = rng.randint(0, 60)
            values = []
            if size:
                values.append(rng.randint(-10_000, 10_000))
                values.extend(
                    None if rng.random() < 0.3 else rng.randint(-10_000, 10_000)
                    for _ in range(size - 1)
                )
            root = build(values)
            with self.subTest(values=values):
                self.assertEqual(self.solve(root), literal_oracle(root))

    def test_random_balanced_and_perturbed_trees(self):
        rng = random.Random(1101)
        for _ in range(100):
            size = rng.randint(1, 120)
            root = build(list(range(size)))  # complete tree: balanced
            with self.subTest(size=size):
                self.assertEqual(self.solve(root), literal_oracle(root))
                self.assertTrue(self.solve(root))
                # Attach a chain deep down to break the balance.
                node = root
                while node.left is not None:
                    node = node.left
                for _ in range(3):
                    node.left = TreeNode(0, node.left, None)
                    node = node.left
                self.assertEqual(self.solve(root), literal_oracle(root))
                self.assertFalse(self.solve(root))

    def test_constraint_sized(self):
        # 5000 nodes is the constraint maximum.
        big_chain = chain(5000)
        self.assertGreater(balance_of_root_children(big_chain), 1)
        self.assertFalse(self.solve(big_chain))

        left_chain = None
        for _ in range(5000):
            left_chain = TreeNode(0, left_chain, None)
        self.assertGreater(balance_of_root_children(left_chain), 1)
        self.assertFalse(self.solve(left_chain))

        # A perfect tree of 4095 nodes: both children of every node have equal
        # height, so it is balanced.
        perfect_tree = perfect(12)
        self.assertTrue(self.solve(perfect_tree))
        self.assertEqual(self.solve(perfect_tree), literal_oracle(perfect_tree))

        # A complete tree with 5000 nodes (height 13) is balanced too.
        complete = build(list(range(5000)))
        self.assertTrue(self.solve(complete))
        self.assertEqual(self.solve(complete), literal_oracle(complete))

        # The perfect tree plus a three-node chain at its deepest-left leaf is
        # not: that leaf's subtree grows to height 3 while its sibling stays 0.
        broken = perfect(12)
        node = broken
        for _ in range(11):
            node = node.left
        for _ in range(3):
            node.left = TreeNode(0, node.left, None)
            node = node.left
        self.assertGreater(balance_of_root_children(broken), 1)
        self.assertFalse(self.solve(broken))


if __name__ == '__main__':
    unittest.main()
