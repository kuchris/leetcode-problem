"""Tests for 112. Path Sum.

Oracle: enumerate *every* root-to-leaf path sum by plain recursion (collect sums
of leaf paths, then ask whether the target is among them). It never short
circuits, so it is a different program from the solution's early-exit DFS, and it
makes the two easy mistakes visible:

  - an empty tree has no paths, so [] with targetSum = 0 is False;
  - the path must end at a leaf, so [1, 2] with targetSum = 1 is False even
    though the root alone sums to 1.
"""

import itertools
import random
import unittest

from _loader import load_solution
from _trees import TreeNode, build, from_structure

Solution = load_solution('112-path-sum.py').Solution


def all_path_sums(node, prefix: int = 0) -> list:
    if node is None:
        return []
    total = prefix + node.val
    if node.left is None and node.right is None:
        return [total]
    return all_path_sums(node.left, total) + all_path_sums(node.right, total)


def oracle(root, target: int) -> bool:
    return target in all_path_sums(root)


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


def chained(size: int, value: int = 0):
    """Level-order list of a right-leaning chain."""
    values = []
    for _ in range(size):
        values.append(value)
        values.append(None)
    values.pop()
    return values


class PathSumTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().hasPathSum

    def check(self, values, target):
        root = build(values)
        self.assertEqual(self.solve(root, target), oracle(root, target))
        return self.solve(root, target)

    def test_official_examples(self):
        self.assertTrue(self.check(
            [5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1], 22))
        self.assertFalse(self.check([1, 2, 3], 5))
        self.assertFalse(self.check([], 0))

    def test_empty_tree_has_no_paths(self):
        self.assertFalse(self.solve(None, 0))
        self.assertFalse(self.solve(None, 1))
        self.assertFalse(self.solve(None, -1000))

    def test_path_must_end_at_a_leaf(self):
        # The root sums to 1 but is not a leaf.
        self.assertFalse(self.check([1, 2], 1))
        self.assertFalse(self.check([1, None, 2], 1))
        # A prefix match in the middle of a chain does not count either.
        self.assertFalse(self.check([1, 2, None, 3], 3))
        self.assertTrue(self.check([1, 2, None, 3], 6))
        self.assertTrue(self.check([1, 2, None, 3], 1 + 2 + 3))

    def test_single_node(self):
        self.assertTrue(self.check([0], 0))
        self.assertTrue(self.check([-1000], -1000))
        self.assertTrue(self.check([1000], 1000))
        self.assertFalse(self.check([1000], 0))

    def test_negative_values(self):
        # [1, -2, -3] has exactly two root-to-leaf paths: -1 and -2.
        self.assertTrue(self.check([-2, None, -3], -5))
        self.assertTrue(self.check([1, -2, -3], -1))
        self.assertTrue(self.check([1, -2, -3], -2))
        self.assertFalse(self.check([1, -2, -3], -3))
        self.assertFalse(self.check([1, -2, -3], 1))

    def test_deep_chain_prefix_does_not_count(self):
        size = 200
        values = chained(size, 5)
        self.assertTrue(self.check(values, 1000))
        self.assertFalse(self.check(values, 995))  # ends one node too early
        self.assertFalse(self.check(values, 0))

    def test_exhaustive_small_cases(self):
        targets = (-2, -1, 0, 1, 2)
        for size in range(0, 5):
            for shape in all_shapes(size):
                for values in itertools.product((-1, 0, 1), repeat=size):
                    root = from_structure(fill(shape, values))
                    for target in targets:
                        with self.subTest(size=size, values=values, target=target):
                            self.assertEqual(self.solve(root, target), oracle(root, target))
        for shape in all_shapes(5):
            for values in itertools.product((0, 1), repeat=5):
                root = from_structure(fill(shape, values))
                for target in targets:
                    with self.subTest(size=5, values=values, target=target):
                        self.assertEqual(self.solve(root, target), oracle(root, target))

    def test_random_cases(self):
        rng = random.Random(1120)
        for _ in range(400):
            size = rng.randint(0, 200)
            values = []
            if size:
                values.append(rng.randint(-1000, 1000))
                values.extend(
                    None if rng.random() < 0.3 else rng.randint(-1000, 1000)
                    for _ in range(size - 1)
                )
            root = build(values)
            target = rng.randint(-1000, 1000)
            with self.subTest(size=size, target=target):
                self.assertEqual(self.solve(root, target), oracle(root, target))

    def test_random_matching_targets(self):
        # Target taken from a real path, so the answer must be True.
        rng = random.Random(1121)
        for _ in range(200):
            size = rng.randint(1, 60)
            root = build(list(rng.randint(-3, 3) for _ in range(size)))
            sums = all_path_sums(root)
            target = rng.choice(sums)
            with self.subTest(size=size, target=target):
                self.assertTrue(self.solve(root, target))
                self.assertEqual(self.solve(root, target), oracle(root, target))

    def test_constraint_sized(self):
        # 5000 nodes is the constraint maximum; targetSum stays within [-1000, 1000].
        zeros = build(chained(5000))
        self.assertTrue(self.solve(zeros, 0))
        self.assertFalse(self.solve(zeros, 1))
        self.assertFalse(self.solve(zeros, -1))

        fives = build(chained(200, 5))
        self.assertTrue(self.solve(fives, 1000))
        self.assertFalse(self.solve(fives, 995))

        # A complete tree with 4095 nodes of value 1: every root-to-leaf path has
        # 12 nodes, so 12 is reachable and 13 is not.
        complete = build([1] * 4095)
        self.assertTrue(self.solve(complete, 12))
        self.assertFalse(self.solve(complete, 13))
        self.assertFalse(self.solve(complete, -12))

        # Same tree, one leaf made negative: the paths through it sum to -7,
        # every other path still sums to 0.
        mixed = build([0] * 4095)
        node = mixed
        while node.left is not None:
            node = node.left
        node.val = -7
        self.assertTrue(self.solve(mixed, 0))
        self.assertTrue(self.solve(mixed, -7))
        self.assertFalse(self.solve(mixed, -1))


if __name__ == '__main__':
    unittest.main()
