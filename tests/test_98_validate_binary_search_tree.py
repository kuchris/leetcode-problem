"""Tests for 98. Validate Binary Search Tree.

Oracles:
  - ``literal_oracle``: translates the definition word for word — for every node,
    collect the values of its left subtree and require all of them to be
    smaller, and the values of its right subtree to be all larger, then recurse.
    It is O(n^2) and never walks in inorder, so it shares no reasoning with the
    solution (which scans the inorder sequence).
  - ``range_check``: an iterative (low, high) window check, used for the
    10^4-node cases where the quadratic oracle is too slow.

The classic traps are covered: a deep node violating an ancestor (not just its
parent) and duplicate keys.
"""

import itertools
import random
import unittest

from _loader import load_solution
from _trees import TreeNode, build, from_structure

Solution = load_solution('98-validate-binary-search-tree.py').Solution

INT_MIN = -(2 ** 31)
INT_MAX = 2 ** 31 - 1


def subtree_values(root) -> list:
    if root is None:
        return []
    return [root.val] + subtree_values(root.left) + subtree_values(root.right)


def literal_oracle(root) -> bool:
    """The problem statement, transcribed: subtree-wise comparison, O(n^2)."""
    if root is None:
        return True
    if any(value >= root.val for value in subtree_values(root.left)):
        return False
    if any(value <= root.val for value in subtree_values(root.right)):
        return False
    return literal_oracle(root.left) and literal_oracle(root.right)


def range_check(root) -> bool:
    """Iterative (low, high) window check; None means unbounded."""
    stack = [(root, None, None)]
    while stack:
        node, low, high = stack.pop()
        if node is None:
            continue
        if low is not None and node.val <= low:
            return False
        if high is not None and node.val >= high:
            return False
        stack.append((node.left, low, node.val))
        stack.append((node.right, node.val, high))
    return True


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


def balanced_tree(sorted_values) -> "TreeNode | None":
    """A perfectly balanced BST over sorted distinct values."""
    if not sorted_values:
        return None
    middle = len(sorted_values) // 2
    return TreeNode(
        sorted_values[middle],
        balanced_tree(sorted_values[:middle]),
        balanced_tree(sorted_values[middle + 1:]),
    )


def leftmost(node) -> "TreeNode":
    while node.left is not None:
        node = node.left
    return node


class ValidateBinarySearchTreeTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().isValidBST

    def check(self, values):
        return self.solve(build(values))

    def test_official_examples(self):
        self.assertTrue(self.check([2, 1, 3]))
        self.assertFalse(self.check([5, 1, 4, None, None, 3, 6]))

    def test_single_node_and_empty(self):
        self.assertTrue(self.check([1]))
        self.assertTrue(self.check([0]))
        self.assertTrue(self.check([INT_MAX]))
        self.assertTrue(self.check([INT_MIN]))
        self.assertTrue(self.solve(None))

    def test_deep_violation_not_just_parent(self):
        # 6 sits in the right subtree of 10 but is smaller than 10.
        self.assertFalse(self.check([10, 5, 15, None, None, 6, 20]))
        # 3 sits in the right subtree of 5 (via 6) but is smaller than 5.
        self.assertFalse(self.check([5, 4, 6, None, None, 3, 7]))
        # A valid tree with the same shape but consistent values.
        self.assertTrue(self.check([5, 4, 7, None, None, 6, 8]))

    def test_duplicates_are_rejected(self):
        self.assertFalse(self.check([1, 1]))
        self.assertFalse(self.check([2, 1, 1]))
        self.assertFalse(self.check([2, 2, 3]))
        self.assertFalse(self.check([1, None, 1]))
        # Equal values are fine nowhere, not even far apart.
        self.assertFalse(self.check([3, 1, 5, 0, 2, 4, 3]))
        self.assertTrue(self.check([3, 1, 5, 0, 2, 4, 6]))

    def test_skewed_trees(self):
        self.assertTrue(self.check([1, None, 2, None, 3, None, 4]))
        self.assertTrue(self.check([4, 3, None, 2, None, 1]))
        self.assertFalse(self.check([1, None, 2, None, 1]))
        self.assertFalse(self.check([4, 3, None, 5, None, 1]))

    def test_boundary_values(self):
        self.assertTrue(self.check([0, INT_MIN, INT_MAX]))
        self.assertTrue(self.check([INT_MAX - 1, INT_MIN, INT_MAX]))
        self.assertFalse(self.check([0, 1, INT_MAX]))

    def test_exhaustive_small_cases(self):
        for size in range(0, 5):
            for shape in all_shapes(size):
                for values in itertools.product(range(3), repeat=size):
                    with self.subTest(size=size, values=values):
                        root = from_structure(fill(shape, values))
                        self.assertEqual(self.solve(root), literal_oracle(root))
        # Every 5-node shape over a two-value alphabet (so duplicates appear).
        for shape in all_shapes(5):
            for values in itertools.product(range(2), repeat=5):
                with self.subTest(size=5, values=values):
                    root = from_structure(fill(shape, values))
                    self.assertEqual(self.solve(root), literal_oracle(root))

    def test_random_level_order_trees(self):
        rng = random.Random(980)
        for _ in range(600):
            size = rng.randint(0, 40)
            values = []
            if size:
                # Level-order input never starts with a null root.
                values.append(rng.randint(-5, 5))
                values.extend(
                    None if rng.random() < 0.25 else rng.randint(-5, 5)
                    for _ in range(size - 1)
                )
            root = build(values)
            with self.subTest(values=values):
                self.assertEqual(self.solve(root), literal_oracle(root))

    def test_random_bst_and_perturbed_bst(self):
        rng = random.Random(981)
        for _ in range(200):
            numbers = rng.sample(range(-1000, 1000), rng.randint(1, 40))
            root = balanced_tree(sorted(numbers))
            with self.subTest(numbers=numbers):
                self.assertTrue(self.solve(root))
                self.assertEqual(self.solve(root), literal_oracle(root))
                # Perturb one value and compare with the literal oracle.
                node = rng.choice(subtree_nodes(root))
                node.val = rng.randint(-1000, 1000)
                self.assertEqual(self.solve(root), literal_oracle(root))

    def test_constraint_sized(self):
        # 10^4 nodes is the constraint maximum.
        values = list(range(10_000))

        valid = balanced_tree(values)
        self.assertTrue(self.solve(valid))
        self.assertTrue(range_check(valid))

        # The deepest left node is a leaf, so pushing it above every ancestor
        # must break the tree.
        broken = balanced_tree(values)
        victim = leftmost(broken)
        victim.val = INT_MAX
        self.assertFalse(self.solve(broken))
        self.assertFalse(range_check(broken))

        # A 10^4-node right chain of increasing keys is a valid BST.
        chain_values = []
        for value in values:
            chain_values.append(value)
            chain_values.append(None)
        chain_values.pop()
        chain = build(chain_values)
        self.assertTrue(self.solve(chain))
        self.assertTrue(range_check(chain))

        # The mirrored left chain, decreasing keys, is valid too.
        left_values = []
        for value in reversed(values):
            left_values.append(value)
            left_values.append(None)
        left_values.pop()
        left_chain = TreeNode(left_values[0])
        node = left_chain
        for value in left_values[2::2]:
            node.left = TreeNode(value)
            node = node.left
        self.assertTrue(self.solve(left_chain))
        self.assertTrue(range_check(left_chain))

        # A 10^4-node chain with one inversion.
        broken_chain_values = list(chain_values)
        broken_chain_values[-1] = 5_000
        self.assertFalse(self.solve(build(broken_chain_values)))


def subtree_nodes(root) -> list:
    if root is None:
        return []
    return [root, *subtree_nodes(root.left), *subtree_nodes(root.right)]


if __name__ == '__main__':
    unittest.main()
