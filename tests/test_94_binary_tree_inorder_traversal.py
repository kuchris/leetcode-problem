"""Tests for 94. Binary Tree Inorder Traversal.

Oracles:
  - a plain recursive inorder walk (the solution is the iterative version, so
    recursion is a deliberately different code path);
  - the BST property: inserting values into a BST and walking it in inorder must
    reproduce the sorted values, which checks the traversal order itself and not
    just agreement with another walk.

Exhaustive sweep: every tree shape with up to four nodes, over values from
{0, 1, 2}.
"""

import itertools
import random
import unittest

from _loader import load_solution
from _trees import TreeNode, build, from_structure

Solution = load_solution('94-binary-tree-inorder-traversal.py').Solution


def recursive_inorder(root) -> list[int]:
    if root is None:
        return []
    return recursive_inorder(root.left) + [root.val] + recursive_inorder(root.right)


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
    if shape is None:
        return None
    left, right = shape
    iterator = iter(values)
    # Values are consumed in pre-order to match the (value, left, right) layout.
    def place(node):
        if node is None:
            return None
        node_left, node_right = node
        return (next(iterator), place(node_left), place(node_right))
    return place((left, right))


def insert(root, value):
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


class BinaryTreeInorderTraversalTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().inorderTraversal

    def check(self, values):
        return self.solve(build(values))

    def test_official_examples(self):
        self.assertEqual(self.check([1, None, 2, 3]), [1, 3, 2])
        self.assertEqual(
            self.check([1, 2, 3, 4, 5, None, 8, None, None, 6, 7, 9]),
            [4, 2, 6, 5, 7, 1, 3, 9, 8],
        )
        self.assertEqual(self.check([]), [])
        self.assertEqual(self.check([1]), [1])

    def test_single_and_two_nodes(self):
        self.assertEqual(self.check([5]), [5])
        self.assertEqual(self.check([1, 2]), [2, 1])
        self.assertEqual(self.check([1, None, 2]), [1, 2])

    def test_skewed_trees(self):
        # Right chain: inorder is the insertion order.
        right_chain = [1, None, 2, None, 3, None, 4]
        self.assertEqual(self.check(right_chain), [1, 2, 3, 4])
        # Left chain: inorder is the reverse of the level-order values.
        left_chain = [4, 3, None, 2, None, 1]
        self.assertEqual(self.check(left_chain), [1, 2, 3, 4])

    def test_negative_and_boundary_values(self):
        self.assertEqual(self.check([0, -100, 100]), [-100, 0, 100])
        self.assertEqual(self.check([-100]), [-100])

    def test_duplicate_values(self):
        self.assertEqual(self.check([2, 2, 2]), [2, 2, 2])
        self.assertEqual(self.check([1, 1, None, 1]), [1, 1, 1])

    def test_exhaustive_small_cases(self):
        for size in range(0, 5):
            for shape in all_shapes(size):
                for values in itertools.product(range(3), repeat=size):
                    with self.subTest(size=size, values=values):
                        root = from_structure(fill(shape, values))
                        self.assertEqual(
                            self.solve(root), recursive_inorder(root)
                        )

    def test_random_trees_match_recursion(self):
        rng = random.Random(940)
        for _ in range(300):
            size = rng.randint(0, 60)
            values = [rng.randint(-100, 100) for _ in range(size)]
            root = build(values)
            with self.subTest(size=size):
                self.assertEqual(self.solve(root), recursive_inorder(root))

    def test_bst_inorder_is_sorted(self):
        rng = random.Random(941)
        for _ in range(100):
            numbers = rng.sample(range(-1000, 1000), rng.randint(1, 100))
            root = None
            for value in numbers:
                root = insert(root, value)
            with self.subTest(values=numbers):
                self.assertEqual(self.solve(root), sorted(numbers))

    def test_constraint_sized(self):
        # 100 nodes is the constraint maximum.
        rng = random.Random(942)

        # A 100-node right chain: values are emitted in level order.
        values = []
        for value in range(1, 101):
            values.append(value)
            values.append(None)
        values.pop()
        root = build(values)
        self.assertEqual(self.solve(root), list(range(1, 101)))
        self.assertEqual(root.left, None)
        self.assertEqual(self.solve(root), recursive_inorder(root))

        # A random 100-node tree checked against the recursive walk.
        values = [rng.randint(-100, 100) for _ in range(100)]
        root = build(values)
        self.assertEqual(self.solve(root), recursive_inorder(root))

        # A 100-node balanced BST: inorder must be the sorted values.
        numbers = rng.sample(range(-1000, 1000), 100)
        root = None
        for value in numbers:
            root = insert(root, value)
        self.assertEqual(self.solve(root), sorted(numbers))


if __name__ == '__main__':
    unittest.main()
