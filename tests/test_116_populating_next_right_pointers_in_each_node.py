"""Tests for 116. Populating Next Right Pointers in Each Node.

The oracle never looks at a next pointer: it walks the tree level by level with a
BFS queue over ``left``/``right`` only, producing the left-to-right order of each
level. After ``connect``, following the ``next`` chain from the first node of
every level must reproduce exactly that order, node object by node object, and
must end with None.

Recomputing the levels after the call also proves the tree itself was not
reshaped, and the answer is additionally checked against LeetCode's printed
``1,#,2,3,#,4,5,6,7,#`` serialization. Only perfect trees are used, which is what
the statement guarantees.
"""

import random
import unittest

from _loader import load_solution


class Node:
    """Stand-in for the Node that LeetCode injects via its preamble."""

    def __init__(self, val: int = 0, left=None, right=None, next=None):
        self.val = val
        self.left = left
        self.right = right
        self.next = next


module = load_solution('116-populating-next-right-pointers-in-each-node.py')
module.Node = Node
Solution = module.Solution


def perfect_tree(height: int, values=None) -> "Node | None":
    """Build a perfect tree of the given height, filling values in level order."""
    if height <= 0:
        return None
    total = 2 ** height - 1
    if values is None:
        values = list(range(1, total + 1))
    values = list(values)
    assert len(values) == total

    index = 0
    root = Node(values[index])
    index += 1
    current = [root]
    while index < total:
        following = []
        for node in current:
            node.left = Node(values[index])
            index += 1
            node.right = Node(values[index])
            index += 1
            following.append(node.left)
            following.append(node.right)
        current = following
    return root


def levels(root) -> list:
    """Left-to-right node list of every level, using only left/right."""
    if root is None:
        return []
    result = []
    current = [root]
    while current:
        result.append(list(current))
        following = []
        for node in current:
            for child in (node.left, node.right):
                if child is not None:
                    following.append(child)
        current = following
    return result


def serialize_with_next(root) -> list:
    """LeetCode's output format: each level's next chain, '#' terminated."""
    if root is None:
        return []
    out = []
    level_start = root
    while level_start is not None:
        node = level_start
        while node is not None:
            out.append(node.val)
            node = node.next
        out.append('#')
        level_start = level_start.left
    return out


class PopulatingNextRightPointersTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().connect

    def check(self, height, values=None):
        root = perfect_tree(height, values)
        expected_levels = levels(root)
        self.assertIs(self.solve(root), root, 'connect must return the root')

        # The tree itself must be unchanged.
        self.assertEqual(levels(root), expected_levels)

        # Each level's next chain must be exactly that level, in order.
        for depth, level in enumerate(expected_levels):
            node = level[0]
            walked = []
            while node is not None:
                self.assertLessEqual(len(walked), len(level),
                                     f'next chain overruns level {depth}')
                walked.append(node)
                node = node.next
            self.assertEqual(walked, level, f'level {depth} chain is wrong')
            self.assertIsNone(level[-1].next)
        return root

    def test_official_example(self):
        root = self.check(3)
        self.assertEqual(serialize_with_next(root), [1, '#', 2, 3, '#', 4, 5, 6, 7, '#'])

    def test_empty_tree(self):
        self.assertIsNone(self.solve(None))

    def test_single_node(self):
        root = self.check(1)
        self.assertIsNone(root.next)
        self.assertEqual(serialize_with_next(root), [1, '#'])

    def test_two_levels(self):
        root = self.check(2, [10, 20, 30])
        self.assertIs(root.left.next, root.right)
        self.assertIsNone(root.right.next)
        self.assertIsNone(root.next)

    def test_all_perfect_heights(self):
        # 2^12 - 1 = 4095 nodes is the constraint maximum.
        for height in range(1, 13):
            with self.subTest(height=height):
                self.check(height)

    def test_random_values_do_not_affect_linking(self):
        rng = random.Random(1160)
        for height in range(1, 8):
            for _ in range(10):
                values = [rng.randint(-1000, 1000) for _ in range(2 ** height - 1)]
                with self.subTest(height=height):
                    self.check(height, values)

    def test_next_pointers_are_initially_none(self):
        root = perfect_tree(3)
        stack = [root]
        while stack:
            node = stack.pop()
            self.assertIsNone(node.next)
            for child in (node.left, node.right):
                if child is not None:
                    stack.append(child)

    def test_every_level_except_the_last_is_linked_across_subtrees(self):
        # The interesting edge is the right child of a node pointing at the left
        # child of its right neighbour, across two different subtrees.
        root = self.check(4)
        node = root.left
        self.assertIs(node.right.next, root.right.left)
        self.assertIs(root.right.left.right.next, root.right.right.left)
        self.assertIsNone(root.right.right.right.next)

    def test_constraint_sized(self):
        height = 12
        values = list(range(2 ** height - 1))
        root = self.check(height, values)
        serialized = serialize_with_next(root)
        self.assertEqual(serialized[-1], '#')
        self.assertEqual(len(serialized), 4095 + 12)
        # Walk the deepest level from its leftmost node to its rightmost one.
        deepest = root
        while deepest.left is not None:
            deepest = deepest.left
        rightmost = deepest
        while rightmost.next is not None:
            rightmost = rightmost.next
        self.assertEqual(rightmost.val, values[-1])
        self.assertIsNone(rightmost.next)

    def test_cycles_are_not_created(self):
        # A height-10 perfect tree ends in a level of 2^9 = 512 nodes.
        root = self.check(10)
        node = root
        while node.left is not None:
            node = node.left
        seen = 0
        while node is not None:
            seen += 1
            self.assertLessEqual(seen, 512)
            node = node.next
        self.assertEqual(seen, 512)


if __name__ == '__main__':
    unittest.main()
