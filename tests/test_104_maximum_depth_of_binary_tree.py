"""Tests for 104. Maximum Depth of Binary Tree.

Two oracles, neither of them a breadth-first level count:

  - `dfs_depth` walks with an explicit stack of (node, depth) pairs and keeps the
    largest depth seen -- a depth-first traversal, the opposite strategy from the
    solution;
  - `geometric_depth` reuses the (depth, index) labelling of the nodes and takes
    one plus the largest depth label.

Both are iterative so the deep constraint-sized chains stay checkable.
"""

import random
import unittest

from _loader import load_solution
from _trees import TreeNode, from_structure

module = load_solution('104-maximum-depth-of-binary-tree.py')
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


def dfs_depth(root) -> int:
    """Longest root-to-node path, depth first, without recursion."""
    if root is None:
        return 0
    best = 0
    stack = [(root, 1)]
    while stack:
        node, depth = stack.pop()
        if depth > best:
            best = depth
        if node.left is not None:
            stack.append((node.left, depth + 1))
        if node.right is not None:
            stack.append((node.right, depth + 1))
    return best


def geometric_depth(root) -> int:
    """One plus the largest (depth, index) label, computed level by level."""
    if root is None:
        return 0
    depth = 0
    level = [(root, 0)]
    while level:
        depth += 1
        following = []
        for node, index in level:
            if node.left is not None:
                following.append((node.left, 2 * index))
            if node.right is not None:
                following.append((node.right, 2 * index + 1))
        level = following
    return depth


def random_structure(rng, size: int):
    """A random binary tree with `size` nodes, as a nested (value, l, r) tuple.

    Splitting the node count at a random point avoids enumerating shapes, which
    is only feasible for single-digit sizes.
    """
    if size == 0:
        return None
    left_size = rng.randint(0, size - 1)
    return (rng.randint(-100, 100),
            random_structure(rng, left_size),
            random_structure(rng, size - 1 - left_size))


def chain(size: int, to_the_left: bool = True, value: int = 0) -> TreeNode:
    """A chain of `size` nodes built iteratively (deepest possible shape)."""
    root = None
    for _ in range(size):
        root = TreeNode(value, root, None) if to_the_left else TreeNode(value, None, root)
    return root


def complete_tree(size: int, value: int = 0) -> TreeNode:
    """A complete tree with `size` nodes, built iteratively."""
    root = TreeNode(value)
    queue = [root]
    created = 1
    while created < size:
        node = queue.pop(0)
        node.left = TreeNode(value)
        created += 1
        queue.append(node.left)
        if created < size:
            node.right = TreeNode(value)
            created += 1
            queue.append(node.right)
    return root


class MaximumDepthOfBinaryTreeTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().maxDepth

    def test_official_examples(self):
        root = from_structure((3, (9, None, None), (20, (15, None, None), (7, None, None))))
        self.assertEqual(self.solve(root), 3)
        self.assertEqual(self.solve(from_structure((1, None, (2, None, None)))), 2)

    def test_empty_and_single(self):
        self.assertEqual(self.solve(None), 0)
        self.assertEqual(self.solve(from_structure((5, None, None))), 1)

    def test_minimum_and_maximum_values(self):
        self.assertEqual(self.solve(from_structure((-100, None, None))), 1)
        self.assertEqual(self.solve(from_structure((100, (0, None, None), None))), 2)

    def test_chains_of_every_length(self):
        for size in range(1, 21):
            with self.subTest(size=size):
                self.assertEqual(self.solve(chain(size, True)), size)
                self.assertEqual(self.solve(chain(size, False)), size)

    def test_shallow_wide_tree_beats_deep_narrow_one(self):
        wide = complete_tree(7)
        self.assertEqual(self.solve(wide), 3)
        self.assertEqual(self.solve(chain(3)), 3)
        self.assertEqual(self.solve(from_structure((1, (2, None, None), (3, None, None)))), 2)

    def test_exhaustive_small_cases(self):
        for size in range(1, 8):
            for shape in shapes(size):
                root = from_structure(fill_preorder(shape, list(range(size))))
                with self.subTest(size=size, values=list(range(size))):
                    self.assertEqual(self.solve(root), dfs_depth(root))
                    self.assertEqual(self.solve(root), geometric_depth(root))

    def test_randomised_cases(self):
        rng = random.Random(1040)
        for _ in range(400):
            size = rng.randint(1, 80)
            root = from_structure(random_structure(rng, size))
            with self.subTest(size=size):
                self.assertEqual(self.solve(root), dfs_depth(root))
                self.assertEqual(self.solve(root), geometric_depth(root))

    def test_constraint_sized(self):
        # 10^4 nodes is the constraint maximum, including the deepest shapes.
        size = 10 ** 4
        self.assertEqual(self.solve(chain(size, True)), size)
        self.assertEqual(self.solve(chain(size, False)), size)

        # 2^14 - 1 > 10^4 >= 2^13, so a complete tree with 10^4 nodes has depth 14.
        complete = complete_tree(size)
        self.assertEqual(self.solve(complete), 14)
        self.assertEqual(dfs_depth(complete), 14)

        # A caterpillar: a spine where every node also carries a leaf. 5000 spine
        # nodes plus 5000 leaves is exactly 10^4 nodes, and the longest path is
        # the spine plus the leaf hanging off its deepest node.
        spine = None
        for _ in range(size // 2):
            node = TreeNode(0)
            node.left = spine
            node.right = TreeNode(0)
            spine = node
        self.assertEqual(self.solve(spine), size // 2 + 1)
        self.assertEqual(dfs_depth(spine), size // 2 + 1)


if __name__ == '__main__':
    unittest.main()
