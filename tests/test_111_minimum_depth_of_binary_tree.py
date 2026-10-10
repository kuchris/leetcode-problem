"""Tests for 111. Minimum Depth of Binary Tree.

Oracle: the definition as plain DFS -- depth 0 for a missing node, 1 for a node
with no children, otherwise 1 + min over the children that actually exist. The
solution is breadth-first, so the oracle shares no mechanism with it.

The leaf trap is covered explicitly: a node with only one child is not a leaf,
so minimum depth is not the mirrored maximum. [1, 2] has minimum depth 2, and the
naive recurrence 1 + min(depth(left), depth(right)) with depth(None) = 0 would
wrongly answer 1. Every trap case below is asserted twice: against a hard-coded
expected value and against the oracle.
"""

import random
import sys
import unittest

from _loader import load_solution
from _trees import TreeNode, build

Solution = load_solution('111-minimum-depth-of-binary-tree.py').Solution

sys.setrecursionlimit(30000)


def dfs_oracle(node) -> int:
    if node is None:
        return 0
    if node.left is None and node.right is None:
        return 1
    best = None
    for child in (node.left, node.right):
        if child is not None:
            depth = dfs_oracle(child)
            if best is None or depth < best:
                best = depth
    return 1 + best


def all_shapes(size):
    if size == 0:
        yield None
        return
    for left_size in range(size):
        for left in all_shapes(left_size):
            for right in all_shapes(size - 1 - left_size):
                yield (left, right)


def chained(size: int, value: int = 0):
    """Build a right-leaning chain level-order list."""
    values = []
    for _ in range(size):
        values.append(value)
        values.append(None)
    values.pop()
    return values


class MinimumDepthOfBinaryTreeTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().minDepth

    def check(self, values):
        root = build(values)
        return self.solve(root)

    def test_official_examples(self):
        self.assertEqual(self.check([3, 9, 20, None, None, 15, 7]), 2)
        self.assertEqual(self.check([2, None, 3, None, 4, None, 5, None, 6]), 5)

    def test_empty_tree(self):
        self.assertEqual(self.check([]), 0)
        self.assertEqual(self.solve(None), 0)

    def test_single_node_is_a_leaf_at_depth_one(self):
        self.assertEqual(self.check([1]), 1)
        self.assertEqual(self.check([-1000]), 1)

    def test_one_child_is_not_a_leaf(self):
        # The trap: [1,2] is a chain of two nodes, so its minimum depth is 2 --
        # not 1, which is what "1 + min(0, depth)" would produce.
        self.assertEqual(self.check([1, 2]), 2)
        self.assertEqual(self.check([1, None, 2]), 2)
        self.assertEqual(self.check([1, 2, None]), 2)
        self.assertEqual(self.check([1, 2, 3]), 2)
        self.assertEqual(self.check([1, 2, None, 3]), 3)
        self.assertEqual(self.check([1, 2, None, 3, None, 4]), 4)
        self.assertEqual(self.check([1, None, 2, None, 3, None, 4]), 4)

    def test_shallow_branch_beats_deep_branch(self):
        # A deep left path exists, but both children of the root are leaves.
        values = [1, 2, 3, None, None, None, None]
        self.assertEqual(self.check(values), 2)
        # A leaf exists at depth 3 on the right, while the left path goes deeper.
        values = [1, 2, 3, 4, None, 5, None]
        self.assertEqual(self.check(values), 3)

    def test_the_trap_cases_against_the_oracle(self):
        traps = [
            [1],
            [1, 2],
            [1, None, 2],
            [1, 2, 3],
            [1, 2, None, 3],
            [1, 2, None, 3, None, 4],
            [1, None, 2, None, 3, None, 4],
            [2, None, 3, None, 4, None, 5, None, 6],
            [1, 2, 3, None, None, None, None],
            [0, 0, 0, 0, None, None, 0, 0, None, None, 0, None, 0, 0, 0],
        ]
        for values in traps:
            with self.subTest(values=values):
                root = build(values)
                self.assertEqual(self.solve(root), dfs_oracle(root))

    def test_exhaustive_shapes_up_to_seven_nodes(self):
        for size in range(0, 8):
            for shape in all_shapes(size):
                tree = shape_tree(shape)
                with self.subTest(size=size, shape=shape):
                    self.assertEqual(self.solve(tree), dfs_oracle(tree))

    def test_random_level_order_trees(self):
        rng = random.Random(1110)
        for _ in range(400):
            size = rng.randint(0, 300)
            values = []
            if size:
                values.append(rng.randint(-1000, 1000))
                values.extend(
                    None if rng.random() < 0.35 else rng.randint(-1000, 1000)
                    for _ in range(size - 1)
                )
            root = build(values)
            with self.subTest(values=values[:20]):
                self.assertEqual(self.solve(root), dfs_oracle(root))

    def test_deep_chain_against_the_oracle(self):
        for size in (1, 2, 500, 3000):
            values = chained(size)
            with self.subTest(size=size):
                root = build(values)
                self.assertEqual(self.solve(root), size)
                self.assertEqual(self.solve(root), dfs_oracle(root))

    def test_constraint_sized(self):
        # 10^5 nodes is the constraint maximum.
        size = 100_000
        chain_root = build(chained(size))
        self.assertEqual(self.solve(chain_root), size)

        # A broom: a 50_000-node left chain with one leaf hanging at depth 2.
        broom = build(chained(50_000))
        broom.right = build([0])
        self.assertEqual(self.solve(broom), 2)

        # A perfect tree of 65535 nodes has minimum depth 16.
        perfect = build(list(range(65535)))
        self.assertEqual(self.solve(perfect), 16)
        self.assertEqual(self.solve(perfect), dfs_oracle(perfect))

        # The same deep branch somewhere else does not matter: the right child
        # of the root is a leaf, so the answer is 2 even with a huge left side.
        left_heavy = build(chained(1000))
        left_heavy.right = build([7])
        self.assertEqual(self.solve(left_heavy), 2)


def shape_tree(shape, value=0):
    """Turn a shape into a tree whose values do not affect the answer."""
    if shape is None:
        return None
    left, right = shape
    return TreeNode(value, shape_tree(left, value), shape_tree(right, value))


if __name__ == '__main__':
    unittest.main()
