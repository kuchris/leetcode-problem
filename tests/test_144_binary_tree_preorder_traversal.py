"""Tests for 144. Binary Tree Preorder Traversal.

Oracles:
  - ``recursive_preorder``: a plain recursive visit -- root, left subtree, right
    subtree -- which is a different mechanism from the solution's explicit stack
    (the follow-up asks for the iterative version);
  - the BST property: inserting a sequence of keys into a BST and then traversing
    it in preorder reproduces the insertion sequence, which checks the traversal
    order without any second traversal implementation.

Exhaustive sweep over every tree shape with up to five nodes over values from
{0, 1, 2}.
"""

import itertools
import random
import unittest

from _loader import load_solution
from _trees import TreeNode, build, from_structure, to_structure

Solution = load_solution('144-binary-tree-preorder-traversal.py').Solution


def recursive_preorder(root) -> list[int]:
    if root is None:
        return []
    return [root.val] + recursive_preorder(root.left) + recursive_preorder(root.right)


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


def chained(size: int, value: int = 0, side: str = 'right'):
    if size <= 0:
        return []
    if side == 'right':
        values = []
        for _ in range(size):
            values.extend([value, None])
        values.pop()
        return values
    values = [value]
    for _ in range(size - 1):
        values.extend([value, None])
    return values


class BinaryTreePreorderTraversalTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().preorderTraversal

    def check(self, values):
        root = build(values)
        produced = self.solve(root)
        self.assertEqual(produced, recursive_preorder(root))
        return produced

    def test_official_examples(self):
        self.assertEqual(self.check([1, None, 2, 3]), [1, 2, 3])
        self.assertEqual(
            self.check([1, 2, 3, 4, 5, None, 8, None, None, 6, 7, 9]),
            [1, 2, 4, 5, 6, 7, 3, 8, 9],
        )
        self.assertEqual(self.check([]), [])
        self.assertEqual(self.check([1]), [1])

    def test_empty_and_single_node(self):
        self.assertEqual(self.solve(None), [])
        self.assertEqual(self.check([]), [])
        self.assertEqual(self.check([-100]), [-100])
        self.assertEqual(self.check([100]), [100])

    def test_skewed_trees(self):
        self.assertEqual(self.check([1, None, 2, None, 3, None, 4]), [1, 2, 3, 4])
        self.assertEqual(self.check([4, 3, None, 2, None, 1]), [4, 3, 2, 1])
        self.assertEqual(self.check([1, 2, 3, 4]), [1, 2, 4, 3])

    def test_duplicate_and_boundary_values(self):
        self.assertEqual(self.check([2, 2, 2]), [2, 2, 2])
        self.assertEqual(self.check([0, -100, 100]), [0, -100, 100])
        self.assertEqual(self.check([1, 1, None, 1]), [1, 1, 1])

    def test_exhaustive_small_cases(self):
        for size in range(0, 6):
            for shape in all_shapes(size):
                for values in itertools.product(range(3), repeat=size):
                    root = from_structure(fill(shape, values))
                    with self.subTest(size=size, values=values):
                        self.assertEqual(self.solve(root), recursive_preorder(root))

    def test_random_trees(self):
        rng = random.Random(1440)
        for _ in range(400):
            size = rng.randint(0, 100)
            values = []
            if size:
                values.append(rng.randint(-100, 100))
                values.extend(
                    None if rng.random() < 0.3 else rng.randint(-100, 100)
                    for _ in range(size - 1)
                )
            root = build(values)
            with self.subTest(size=size):
                self.assertEqual(self.solve(root), recursive_preorder(root))

    def test_preorder_rebuilds_the_same_bst(self):
        # A BST is uniquely determined by its preorder, and re-inserting the
        # preorder sequence in order must rebuild exactly the same tree. That
        # checks the traversal order through a property, with no second
        # traversal implementation involved. (Note the insertion sequence that
        # *created* the tree is not generally its preorder: a key can be
        # inserted as a descendant of an earlier key and still be visited
        # before later siblings.)
        rng = random.Random(1441)
        for _ in range(200):
            numbers = rng.sample(range(-1000, 1000), rng.randint(1, 100))
            root = None
            for value in numbers:
                root = insert(root, value)
            preorder = self.solve(root)
            rebuilt = None
            for value in preorder:
                rebuilt = insert(rebuilt, value)
            with self.subTest(size=len(numbers)):
                self.assertEqual(sorted(preorder), sorted(numbers))
                self.assertEqual(to_structure(rebuilt), to_structure(root))

    def test_preorder_of_a_bst_is_a_valid_insertion_order(self):
        # The preorder is exactly the canonical "parent before descendant"
        # insertion order of the tree it came from.
        rng = random.Random(1442)
        for _ in range(100):
            numbers = rng.sample(range(-500, 500), rng.randint(1, 60))
            root = None
            for value in numbers:
                root = insert(root, value)
            rebuilt = None
            for value in self.solve(root):
                rebuilt = insert(rebuilt, value)
            with self.subTest(size=len(numbers)):
                self.assertEqual(recursive_preorder(rebuilt), self.solve(root))

    def test_constraint_sized(self):
        # 100 nodes is the constraint maximum.
        zero_chain = build(chained(100))
        self.assertEqual(self.solve(zero_chain), [0] * 100)
        self.assertEqual(self.solve(zero_chain), recursive_preorder(zero_chain))

        # A right chain whose values increase level by level: preorder is exactly
        # the level-order value sequence.
        increasing = []
        for value in range(100):
            increasing.extend([value, None])
        increasing.pop()
        self.assertEqual(self.solve(build(increasing)), list(range(100)))

        # An all-left chain: preorder is the level-order sequence too (root first,
        # then each left child).
        left_chain = build(chained(100, side='left'))
        self.assertEqual(self.solve(left_chain), recursive_preorder(left_chain))

        complete = build(list(range(100)))
        self.assertEqual(self.solve(complete), recursive_preorder(complete))

        rng = random.Random(1442)
        values = [rng.randint(-100, 100) for _ in range(100)]
        random_tree = build(values)
        self.assertEqual(self.solve(random_tree), recursive_preorder(random_tree))

        # 100 nodes with all values equal.
        self.assertEqual(self.solve(build([5] * 100)), [5] * 100)


if __name__ == '__main__':
    unittest.main()
