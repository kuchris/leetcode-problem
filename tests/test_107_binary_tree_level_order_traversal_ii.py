"""Tests for 107. Binary Tree Level Order Traversal II.

Oracle: geometry instead of traversal. Every node is labelled with
(depth, index inside its level) from the heap convention (left child 2x, right
child 2x + 1); the expected answer is the values at each depth ordered by index,
with the depths visited from the deepest to the root. Nothing in that pipeline
runs the breadth-first walk the solution runs.

`structure_problem` re-derives the contract from the output itself: the deepest
level first, each level left to right, the last level a single root value, and
the level sizes adding up to the node count.
"""

import random
import unittest

from _loader import load_solution
from _trees import TreeNode, from_structure

module = load_solution('107-binary-tree-level-order-traversal-ii.py')
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


def random_structure(rng, size: int):
    """Random tree with `size` nodes, by random splits (no shape enumeration)."""
    if size == 0:
        return None
    left_size = rng.randint(0, size - 1)
    return (rng.randint(-1000, 1000),
            random_structure(rng, left_size),
            random_structure(rng, size - 1 - left_size))


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


def left_to_right(root, depth) -> list:
    row = sorted((index, value) for d, index, value in positional(root) if d == depth)
    return [value for _, value in row]


def oracle(root) -> list[list[int]]:
    entries = positional(root)
    if not entries:
        return []
    depths = sorted({depth for depth, _, _ in entries}, reverse=True)
    return [left_to_right(root, depth) for depth in depths]


def structure_problem(result, root) -> "str | None":
    """Verify the bottom-up contract of `result` against the tree's geometry."""
    entries = positional(root)
    depths = sorted({depth for depth, _, _ in entries}, reverse=True)
    if len(result) != len(depths):
        return f'{len(result)} levels, expected {len(depths)}'
    if sum(len(level) for level in result) != len(entries):
        return 'level sizes do not add up to the node count'
    for position, depth in enumerate(depths):
        expected = left_to_right(root, depth)
        if sorted(result[position]) != sorted(expected):
            return f'level {position} holds the wrong values'
        if result[position] != expected:
            return f'level {position} is not left to right'
    if result and result[-1] != [root.val]:
        return 'the last level is not the root on its own'
    return None


def left_chain(size: int, value: int = 0) -> TreeNode:
    root = None
    for _ in range(size):
        root = TreeNode(value, root, None)
    return root


class BinaryTreeLevelOrderTraversalIITests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().levelOrderBottom

    def test_official_examples(self):
        root = from_structure((3, (9, None, None), (20, (15, None, None), (7, None, None))))
        self.assertEqual(self.solve(root), [[15, 7], [9, 20], [3]])
        self.assertEqual(self.solve(from_structure((1, None, None))), [[1]])
        self.assertEqual(self.solve(None), [])

    def test_empty_and_single(self):
        self.assertEqual(self.solve(None), [])
        self.assertEqual(self.solve(from_structure((-1000, None, None))), [[-1000]])

    def test_deepest_level_comes_first(self):
        root = from_structure((1,
                               (2, (4, None, None), None),
                               (3, None, (5, (6, None, None), None))))
        self.assertEqual(self.solve(root), [[6], [4, 5], [2, 3], [1]])
        self.assertIsNone(structure_problem(self.solve(root), root))

    def test_chains_have_one_value_per_level(self):
        self.assertEqual(self.solve(left_chain(4, 9)), [[9], [9], [9], [9]])

    def test_order_inside_a_level_is_preserved(self):
        root = from_structure((1, (2, None, None), (3, None, None)))
        self.assertEqual(self.solve(root), [[2, 3], [1]])
        self.assertIsNone(structure_problem(self.solve(root), root))

    def test_boundary_values(self):
        root = from_structure((-1000, (1000, None, None), (0, None, None)))
        self.assertEqual(self.solve(root), [[1000, 0], [-1000]])

    def test_exhaustive_small_cases(self):
        for size in range(1, 8):
            for shape in shapes(size):
                for values in (list(range(size)), [7] * size):
                    root = from_structure(fill_preorder(shape, values))
                    with self.subTest(size=size, values=values):
                        result = self.solve(root)
                        self.assertEqual(result, oracle(root))
                        self.assertIsNone(structure_problem(result, root))

    def test_randomised_cases(self):
        rng = random.Random(1070)
        for _ in range(300):
            size = rng.randint(1, 60)
            root = from_structure(random_structure(rng, size))
            with self.subTest(size=size):
                result = self.solve(root)
                self.assertEqual(result, oracle(root))
                self.assertIsNone(structure_problem(result, root))

    def test_randomised_chains(self):
        rng = random.Random(1071)
        for _ in range(50):
            size = rng.randint(1, 40)
            values = [rng.randint(-1000, 1000) for _ in range(size)]
            chain_root = None
            for value in values:
                chain_root = TreeNode(value, chain_root, None)
            with self.subTest(size=size):
                result = self.solve(chain_root)
                self.assertEqual(result, oracle(chain_root))
                self.assertIsNone(structure_problem(result, chain_root))

    def test_constraint_sized(self):
        # 2000 nodes is the constraint maximum; 2000 levels is its deepest shape.
        deep = left_chain(2000, 3)
        result = self.solve(deep)
        self.assertEqual(len(result), 2000)
        self.assertTrue(all(level == [3] for level in result))
        self.assertEqual(result[-1], [3])

        size = 2000
        complete = TreeNode(0)
        queue = [complete]
        counter = 1
        while counter < size:
            node = queue.pop(0)
            node.left = TreeNode((counter % 2001) - 1000)
            counter += 1
            queue.append(node.left)
            if counter < size:
                node.right = TreeNode((counter % 2001) - 1000)
                counter += 1
                queue.append(node.right)

        result = self.solve(complete)
        self.assertEqual([len(level) for level in reversed(result)],
                         [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 977])
        self.assertEqual(result[-1], [0])
        self.assertIsNone(structure_problem(result, complete))


if __name__ == '__main__':
    unittest.main()
