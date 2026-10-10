"""Tests for 145. Binary Tree Postorder Traversal.

Oracles:
  - ``recursive_postorder``: the straightforward recursive walk, a deliberately
    different control flow from the stack-based solution under test.
  - ``rebuild_bst``: for a BST with distinct keys the postorder sequence
    determines the tree, so rebuilding the BST from the solution's output and
    comparing shapes checks the order itself rather than agreement with another
    walk. It uses no sorting and no second traversal of the original tree.

Exhaustive sweep: every binary tree shape with up to six nodes, values placed in
pre-order so each shape is distinguishable. Constraint-sized cases use the
maximum of 100 nodes for a complete tree, both chains and a zigzag.
"""

import itertools
import random
import unittest

from _loader import load_solution
from _trees import TreeNode, build, from_structure, to_structure

Solution = load_solution('145-binary-tree-postorder-traversal.py').Solution

MAX_NODES = 100


def recursive_postorder(root) -> list[int]:
    if root is None:
        return []
    return recursive_postorder(root.left) + recursive_postorder(root.right) + [root.val]


def rebuild_bst(postorder) -> "TreeNode | None":
    """Rebuild the BST whose postorder this is; the last value is the root.

    ``build(low, high)`` consumes values from the right while they fit the open
    interval, so a sequence that is not a valid BST postorder yields a smaller
    tree instead of a wrong one.
    """
    index = len(postorder) - 1

    def build_interval(low, high):
        nonlocal index
        if index < 0:
            return None
        value = postorder[index]
        if not low < value < high:
            return None
        index -= 1
        node = TreeNode(value)
        node.right = build_interval(value, high)
        node.left = build_interval(low, value)
        return node

    return build_interval(float('-inf'), float('inf'))


def all_shapes(size):
    """Every binary tree shape with `size` nodes, as nested (left, right) pairs."""
    if size == 0:
        yield None
        return
    for left_size in range(size):
        for left in all_shapes(left_size):
            for right in all_shapes(size - 1 - left_size):
                yield (left, right)


def fill(shape, values):
    """Place `values` over a shape in pre-order, matching (val, left, right)."""
    iterator = iter(values)

    def place(node):
        if node is None:
            return None
        left, right = node
        return (next(iterator), place(left), place(right))

    return place(shape)


def balanced_bst(sorted_values) -> "TreeNode | None":
    if not sorted_values:
        return None
    middle = len(sorted_values) // 2
    return TreeNode(
        sorted_values[middle],
        balanced_bst(sorted_values[:middle]),
        balanced_bst(sorted_values[middle + 1:]),
    )


def insert_bst(root, value) -> "TreeNode":
    if root is None:
        return TreeNode(value)
    node = root
    while True:
        if value < node.val:
            if node.left is None:
                node.left = TreeNode(value)
                return root
            node = node.left
        else:
            if node.right is None:
                node.right = TreeNode(value)
                return root
            node = node.right


class BinaryTreePostorderTraversalTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().postorderTraversal

    def test_official_examples(self):
        self.assertEqual(self.solve(build([1, None, 2, 3])), [3, 2, 1])
        self.assertEqual(
            self.solve(build([1, 2, 3, 4, 5, None, 8, None, None, 6, 7, 9])),
            [4, 6, 7, 5, 2, 9, 8, 3, 1],
        )
        self.assertEqual(self.solve(build([])), [])
        self.assertEqual(self.solve(build([1])), [1])

    def test_empty_and_single_node(self):
        self.assertEqual(self.solve(None), [])
        self.assertEqual(self.solve(TreeNode(-100)), [-100])
        self.assertEqual(self.solve(TreeNode(100)), [100])

    def test_chains(self):
        # A right chain is visited deepest-first.
        self.assertEqual(self.solve(build([1, None, 2, None, 3])), [3, 2, 1])
        # A left chain is already in postorder.
        self.assertEqual(self.solve(build([1, 2, None, 3, None])), [3, 2, 1])
        # The root is always last.
        for values in ([1, 2, 3], [1, 2, None, 3, 4], [5, None, 6, None, 7]):
            result = self.solve(build(values))
            with self.subTest(values=values):
                self.assertEqual(result[-1], values[0])

    def test_exhaustive_shapes_up_to_six_nodes(self):
        for size in range(0, 7):
            for shape in all_shapes(size):
                values = list(range(1, size + 1))
                root = from_structure(fill(shape, values))
                with self.subTest(size=size, shape=shape):
                    self.assertEqual(self.solve(root), recursive_postorder(root))

    def test_bst_reconstruction_oracle(self):
        # Distinct keys: the postorder determines the BST, so the rebuilt tree
        # must have exactly the original shape.
        rng = random.Random(1450)
        for _ in range(300):
            size = rng.randint(1, 12)
            values = rng.sample(range(-100, 100), size)
            root = None
            for value in values:
                root = insert_bst(root, value)
            with self.subTest(values=values):
                result = self.solve(root)
                self.assertEqual(result, recursive_postorder(root))
                self.assertEqual(to_structure(rebuild_bst(result)), to_structure(root))

        # The balanced shapes of 100 distinct keys too.
        for size in (50, 99, 100):
            root = balanced_bst(list(range(size)))
            result = self.solve(root)
            self.assertEqual(to_structure(rebuild_bst(result)), to_structure(root))

    def test_random_trees_against_the_recursive_walk(self):
        rng = random.Random(1451)
        for _ in range(300):
            size = rng.randint(1, 40)
            values = [rng.randint(-100, 100)]
            values.extend(
                None if rng.random() < 0.3 else rng.randint(-100, 100)
                for _ in range(size - 1)
            )
            root = build(values)
            with self.subTest(values=values[:10]):
                self.assertEqual(self.solve(root), recursive_postorder(root))

    def test_constraint_sized(self):
        # A complete tree with the maximum 100 nodes.
        complete = build(list(range(1, MAX_NODES + 1)))
        self.assertEqual(self.solve(complete), recursive_postorder(complete))
        self.assertEqual(len(self.solve(complete)), MAX_NODES)

        # The two degenerate chains of 100 nodes.
        right_chain = [1]
        for value in range(2, MAX_NODES + 1):
            right_chain += [None, value]
        left_chain = [1]
        for value in range(2, MAX_NODES + 1):
            left_chain += [value, None]
        for values in (right_chain, left_chain):
            root = build(values)
            with self.subTest(shape=values[:6], length=len(values)):
                self.assertEqual(self.solve(root), recursive_postorder(root))
                self.assertEqual(sorted(self.solve(root)), list(range(1, MAX_NODES + 1)))

        # A zigzag: every node has exactly one child, alternating sides.
        zigzag = TreeNode(1)
        node = zigzag
        for value in range(2, MAX_NODES + 1):
            child = TreeNode(value)
            if value % 2 == 0:
                node.left = child
            else:
                node.right = child
            node = child
        self.assertEqual(self.solve(zigzag), recursive_postorder(zigzag))
        self.assertEqual(sorted(self.solve(zigzag)), list(range(1, MAX_NODES + 1)))


if __name__ == '__main__':
    unittest.main()
