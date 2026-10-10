"""Tests for 103. Binary Tree Zigzag Level Order Traversal.

The oracle does not run a traversal at all. Every node is labelled with
(depth, index inside its level) from the heap convention (left child 2x, right
child 2x + 1), and a level is produced by sorting those labels: ascending for
even depths, descending for odd depths. Ordering by position is what makes the
zigzag direction checkable without re-running the same breadth-first walk.

`structure_problem` then re-derives the zigzag contract from the *output* alone
against that geometry: right number of levels, right values per level, and the
right direction per level.
"""

import random
import unittest

from _loader import load_solution
from _trees import TreeNode, from_structure

module = load_solution('103-binary-tree-zigzag-level-order-traversal.py')
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
    result = []
    for depth in range(max(depth for depth, _, _ in entries) + 1):
        row = left_to_right(root, depth)
        result.append(row if depth % 2 == 0 else row[::-1])
    return result


def structure_problem(result, root) -> "str | None":
    """Verify the zigzag contract of `result` against the tree's geometry."""
    entries = positional(root)
    depths = sorted({depth for depth, _, _ in entries})
    if len(result) != len(depths):
        return f'{len(result)} levels, expected {len(depths)}'
    if sum(len(level) for level in result) != len(entries):
        return 'level sizes do not add up to the node count'
    for position, depth in enumerate(depths):
        row = left_to_right(root, depth)
        expected = row if position % 2 == 0 else row[::-1]
        if sorted(result[position]) != sorted(expected):
            return f'level {position} holds the wrong values'
        if result[position] != expected:
            return f'level {position} is in the wrong direction'
    return None


def left_chain(size: int, value: int = 0) -> TreeNode:
    root = None
    for _ in range(size):
        root = TreeNode(value, root, None)
    return root


class BinaryTreeZigzagLevelOrderTraversalTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().zigzagLevelOrder

    def test_official_examples(self):
        root = from_structure((3, (9, None, None), (20, (15, None, None), (7, None, None))))
        self.assertEqual(self.solve(root), [[3], [20, 9], [15, 7]])
        self.assertEqual(self.solve(from_structure((1, None, None))), [[1]])
        self.assertEqual(self.solve(None), [])

    def test_empty_and_single(self):
        self.assertEqual(self.solve(None), [])
        self.assertEqual(self.solve(from_structure((0, None, None))), [[0]])

    def test_direction_alternates_on_a_perfect_tree(self):
        root = from_structure((1,
                               (2, (4, None, None), (5, None, None)),
                               (3, (6, None, None), (7, None, None))))
        self.assertEqual(self.solve(root), [[1], [3, 2], [4, 5, 6, 7]])
        self.assertIsNone(structure_problem(self.solve(root), root))

    def test_depth_four_zigzag(self):
        root = from_structure((1,
                               (2, (4, (8, None, None), (9, None, None)),
                                (5, (10, None, None), (11, None, None))),
                               (3, (6, (12, None, None), (13, None, None)),
                                (7, (14, None, None), (15, None, None)))))
        self.assertEqual(self.solve(root),
                         [[1], [3, 2], [4, 5, 6, 7], [15, 14, 13, 12, 11, 10, 9, 8]])
        self.assertIsNone(structure_problem(self.solve(root), root))

    def test_chains_have_single_node_levels(self):
        chain = left_chain(5, 3)
        self.assertEqual(self.solve(chain), [[3], [3], [3], [3], [3]])
        self.assertIsNone(structure_problem(self.solve(chain), chain))

    def test_equal_values_still_need_the_right_level_count(self):
        root = from_structure((1, (1, (1, None, None), (1, None, None)),
                               (1, (1, None, None), (1, None, None))))
        self.assertEqual(self.solve(root), [[1], [1, 1], [1, 1, 1, 1]])
        self.assertIsNone(structure_problem(self.solve(root), root))

    def test_boundary_values(self):
        root = from_structure((-100, (100, None, None), (0, None, None)))
        self.assertEqual(self.solve(root), [[-100], [0, 100]])
        self.assertIsNone(structure_problem(self.solve(root), root))

    def test_exhaustive_small_cases(self):
        for size in range(1, 8):
            for shape in shapes(size):
                for values in (list(range(size)), [7] * size):
                    root = from_structure(fill_preorder(shape, values))
                    with self.subTest(size=size, values=values):
                        self.assertEqual(self.solve(root), oracle(root))
                        self.assertIsNone(structure_problem(self.solve(root), root))

    def test_randomised_cases(self):
        rng = random.Random(1030)
        for _ in range(300):
            size = rng.randint(1, 60)
            root = from_structure(fill_preorder(rng.choice(shapes(size)),
                                                [rng.randint(-100, 100) for _ in range(size)]))
            with self.subTest(size=size):
                result = self.solve(root)
                self.assertEqual(result, oracle(root))
                self.assertIsNone(structure_problem(result, root))

    def test_constraint_sized(self):
        # 2000 nodes is the constraint maximum; 2000 levels is its deepest shape.
        chain = left_chain(2000, -100)
        result = self.solve(chain)
        self.assertEqual(len(result), 2000)
        self.assertTrue(all(level == [-100] for level in result))

        size = 2000
        complete = TreeNode(0)
        queue = [complete]
        counter = 1
        while counter < size:
            node = queue.pop(0)
            node.left = TreeNode(counter % 201 - 100)
            counter += 1
            queue.append(node.left)
            if counter < size:
                node.right = TreeNode(counter % 201 - 100)
                counter += 1
                queue.append(node.right)

        result = self.solve(complete)
        self.assertEqual([len(level) for level in result],
                         [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 977])
        self.assertIsNone(structure_problem(result, complete))
        # Depth 1 must be right-to-left, so its first value is the right child.
        self.assertEqual(result[1], [complete.right.val, complete.left.val])


if __name__ == '__main__':
    unittest.main()
