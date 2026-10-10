"""Tests for 102. Binary Tree Level Order Traversal.

Oracle: geometry instead of traversal. Every node is labelled with
(depth, index inside its level) using the heap convention (left child 2x, right
child 2x + 1); a level is then the values at that depth sorted by index. Ordering
by position rather than by visit order keeps the oracle independent of any
breadth-first walk, and the test also checks the incidental invariants (level
count, level sizes, every value present exactly once).
"""

import random
import unittest

from _loader import load_solution
from _trees import TreeNode, from_structure

module = load_solution('102-binary-tree-level-order-traversal.py')
Solution = module.Solution


def shapes(size: int) -> list:
    if size == 0:
        return [None]
    out = []
    for left_size in range(size):
        for left in shapes(left_size):
            for right in shapes(size - 1 - left_size):
                out.append((left, right))
    return out


def fill_preorder(shape, values):
    iterator = iter(values)

    def walk(node):
        if node is None:
            return None
        value = next(iterator)
        return (value, walk(node[0]), walk(node[1]))

    return walk(shape)


def positional(root) -> list:
    """[(depth, index_in_level, value)] for every node."""
    entries = []
    if root is None:
        return entries
    level = [(root, 0)]
    depth = 0
    while level:
        for node, index in level:
            entries.append((depth, index, node.val))
        following = []
        for node, index in level:
            if node.left is not None:
                following.append((node.left, 2 * index))
            if node.right is not None:
                following.append((node.right, 2 * index + 1))
        level = following
        depth += 1
    return entries


def oracle(root) -> list[list[int]]:
    entries = positional(root)
    if not entries:
        return []
    result = []
    for depth in range(max(depth for depth, _, _ in entries) + 1):
        row = sorted((index, value) for d, index, value in entries if d == depth)
        result.append([value for _, value in row])
    return result


def random_structure(rng, size: int):
    """A random binary tree with `size` nodes, as a nested (value, l, r) tuple.

    Splitting the node count at a random point avoids enumerating shapes, which
    is only feasible for single-digit sizes.
    """
    if size == 0:
        return None
    left_size = rng.randint(0, size - 1)
    return (rng.randint(-1000, 1000),
            random_structure(rng, left_size),
            random_structure(rng, size - 1 - left_size))


def left_chain(size: int, value: int = 0) -> TreeNode:
    root = None
    for _ in range(size):
        root = TreeNode(value, root, None)
    return root


class BinaryTreeLevelOrderTraversalTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().levelOrder

    def test_official_examples(self):
        root = from_structure((3, (9, None, None), (20, (15, None, None), (7, None, None))))
        self.assertEqual(self.solve(root), [[3], [9, 20], [15, 7]])
        self.assertEqual(self.solve(from_structure((1, None, None))), [[1]])
        self.assertEqual(self.solve(None), [])

    def test_empty_and_single(self):
        self.assertEqual(self.solve(None), [])
        self.assertEqual(self.solve(from_structure((0, None, None))), [[0]])

    def test_chains(self):
        self.assertEqual(self.solve(left_chain(4, 1)), [[1], [1], [1], [1]])
        right = None
        for _ in range(3):
            right = TreeNode(2, None, right)
        self.assertEqual(self.solve(right), [[2], [2], [2]])

    def test_levels_are_not_confused_by_shape(self):
        # A left-leaning and a right-leaning level 2.
        left = from_structure((1, (2, (4, None, None), None), (3, None, None)))
        right = from_structure((1, (2, None, None), (3, None, (5, None, None))))
        self.assertEqual(self.solve(left), [[1], [2, 3], [4]])
        self.assertEqual(self.solve(right), [[1], [2, 3], [5]])

    def test_boundary_values(self):
        root = from_structure((-1000, (1000, None, None), (0, None, None)))
        self.assertEqual(self.solve(root), [[-1000], [1000, 0]])

    def test_exhaustive_small_cases(self):
        for size in range(1, 8):
            for shape in shapes(size):
                for values in (list(range(size)), [7] * size):
                    root = from_structure(fill_preorder(shape, values))
                    with self.subTest(size=size, values=values):
                        self.assertEqual(self.solve(root), oracle(root))

    def test_level_structure_is_intact(self):
        rng = random.Random(1020)
        for _ in range(200):
            size = rng.randint(1, 30)
            root = from_structure(random_structure(rng, size))
            result = self.solve(root)
            expected = oracle(root)
            with self.subTest(size=size):
                self.assertEqual(result, expected)
                self.assertEqual(sum(len(level) for level in result), size)
                self.assertEqual([len(level) for level in result],
                                 [len(level) for level in expected])
                self.assertEqual(result[0], [root.val])

    def test_randomised_cases(self):
        rng = random.Random(1021)
        for _ in range(300):
            size = rng.randint(1, 60)
            root = from_structure(random_structure(rng, size))
            with self.subTest(size=size):
                self.assertEqual(self.solve(root), oracle(root))

    def test_constraint_sized(self):
        # 2000 nodes is the constraint maximum.
        size = 2000

        # The deepest shape: 2000 levels of one node each.
        deep = left_chain(size, 5)
        result = self.solve(deep)
        self.assertEqual(len(result), size)
        self.assertTrue(all(level == [5] for level in result))

        # A complete tree built level by level: 11 levels, the last one partial.
        complete = TreeNode(0)
        queue = [complete]
        index = 1
        while index < size:
            node = queue.pop(0)
            node.left = TreeNode(index % 201 - 100)
            index += 1
            queue.append(node.left)
            if index < size:
                node.right = TreeNode(index % 201 - 100)
                index += 1
                queue.append(node.right)
        result = self.solve(complete)
        self.assertEqual([len(level) for level in result], [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 977])
        self.assertEqual(sum(len(level) for level in result), size)


if __name__ == '__main__':
    unittest.main()
