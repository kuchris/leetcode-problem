"""Tests for 199. Binary Tree Right Side View.

Two independent oracles:

  - `queue_oracle` is the explicit-queue BFS: `collections.deque` with level-size
    bookkeeping, recording the node at index `level_size - 1` of every level;
  - `right_first_dfs` is the opposite traversal: a stack that pushes the left child
    before the right one, so each depth is first reached from the right, and a
    depth -> value map is filled in visit order. It shares no code with the BFS.

`height` supplies the structural check both sweeps assert: the view has exactly
one value per level, i.e. len(view) == height.

`shapes` enumerates every binary-tree shape with up to six nodes (Catalan
numbers 1, 2, 5, 14, 42, 132) and `from_structure` builds them, so the exhaustive
sweep walks real shapes instead of a random sample. `visible_node_is_left_child`
verifies structurally that the value at a given depth is a left child who has no
right sibling -- the case the statement's examples hide.
"""

import collections
import itertools
import random
import unittest

from _loader import load_solution
from _trees import build, from_structure, nodes, to_structure

Solution = load_solution('199-binary-tree-right-side-view.py').Solution


def queue_oracle(root) -> list:
    """Explicit-queue BFS; the last node dequeued at each level is visible."""
    if root is None:
        return []
    view = []
    queue = collections.deque([root])
    while queue:
        level_size = len(queue)
        for index in range(level_size):
            node = queue.popleft()
            if index == level_size - 1:
                view.append(node.val)
            if node.left is not None:
                queue.append(node.left)
            if node.right is not None:
                queue.append(node.right)
    return view


def right_first_dfs(root) -> list:
    """Right-first DFS: the first node reached at a depth is that depth's view."""
    view = {}
    stack = [(root, 0)]
    while stack:
        node, depth = stack.pop()
        if node is None:
            continue
        view.setdefault(depth, node.val)
        stack.append((node.left, depth + 1))  # pushed first, popped last
        stack.append((node.right, depth + 1))
    return [view[depth] for depth in sorted(view)]


def height(root) -> int:
    best = 0
    stack = [(root, 1)]
    while stack:
        node, depth = stack.pop()
        if node is None:
            continue
        best = max(best, depth)
        stack.append((node.left, depth + 1))
        stack.append((node.right, depth + 1))
    return best


def shapes(size: int) -> list:
    """All binary-tree shapes with `size` nodes, as nested (left, right) tuples."""
    if size == 0:
        return [None]
    result = []
    for left_size in range(size):
        for left in shapes(left_size):
            for right in shapes(size - 1 - left_size):
                result.append((left, right))
    return result


def fill(shape, values) -> "TreeNode | None":
    """Build a tree from a shape and a pre-order sequence of node values."""
    iterator = iter(values)

    def convert(node):
        if node is None:
            return None
        return (next(iterator), convert(node[0]), convert(node[1]))

    return from_structure(convert(shape))


def visible_node_is_left_child(root, depth: int) -> bool:
    """True when the only node at 0-based `depth` is a left child."""
    level = [] if root is None else [root]
    current_depth = 0
    while level:
        if current_depth == depth:
            if len(level) != 1:
                return False
            target = level[0]
            return any(node.left is target for node in nodes(root))
        next_level = []
        for node in level:
            if node.left is not None:
                next_level.append(node.left)
            if node.right is not None:
                next_level.append(node.right)
        level = next_level
        current_depth += 1
    return False


class BinaryTreeRightSideViewTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().rightSideView

    def assert_view(self, root) -> list:
        before = to_structure(root)
        result = self.solve(root)
        self.assertEqual(result, queue_oracle(root))
        self.assertEqual(result, right_first_dfs(root))
        self.assertEqual(len(result), height(root), 'one visible value per level')
        self.assertEqual(to_structure(root), before, 'the tree must not be modified')
        return result

    def test_official_examples(self):
        self.assertEqual(self.solve(build([1, 2, 3, None, 5, None, 4])), [1, 3, 4])
        self.assertEqual(self.solve(build([1, 2, 3, 4, None, None, None, 5])), [1, 3, 4, 5])
        self.assertEqual(self.solve(build([1, None, 3])), [1, 3])
        self.assertEqual(self.solve(build([])), [])

    def test_empty_tree(self):
        self.assertEqual(self.solve(None), [])
        self.assertEqual(self.assert_view(None), [])

    def test_single_node(self):
        for value in (-100, -1, 0, 1, 100):
            with self.subTest(value=value):
                self.assertEqual(self.solve(build([value])), [value])

    def test_left_and_right_chains(self):
        # A left spine of four nodes: every level's only node is a left child.
        left_chain = build([1, 2, None, 3, None, 4, None])
        self.assertEqual(self.solve(left_chain), [1, 2, 3, 4])
        self.assertEqual(self.assert_view(left_chain), [1, 2, 3, 4])

        right_chain = build([1, None, 2, None, 3, None, 4])
        self.assertEqual(self.solve(right_chain), [1, 2, 3, 4])
        self.assertEqual(self.assert_view(right_chain), [1, 2, 3, 4])

    def test_visible_node_may_be_a_left_child(self):
        # 3 has no right child, so depth 3 sees 3's left child 4.
        tree = build([1, None, 3, 4])
        self.assertEqual(self.solve(tree), [1, 3, 4])
        self.assertTrue(visible_node_is_left_child(tree, 2))
        self.assertEqual(self.assert_view(tree), [1, 3, 4])

        # Two levels in a row where the visible node is a left child.
        tree = build([1, 2, None, 3, None, 4, None])
        self.assertEqual(self.solve(tree), [1, 2, 3, 4])
        for depth in (1, 2, 3):
            with self.subTest(depth=depth):
                self.assertTrue(visible_node_is_left_child(tree, depth))

        # The left child is deeper than a right child of the same level.
        tree = build([1, 2, 3, 4, None, None, 5])
        self.assertEqual(self.solve(tree), [1, 3, 5])
        self.assertEqual(self.assert_view(tree), [1, 3, 5])

    def test_rightmost_node_shadows_its_left_sibling(self):
        tree = build([1, 2, 3, 4, 5, 6, 7])
        self.assertEqual(self.solve(tree), [1, 3, 7])
        tree = build([1, 2, 3, 4, 5, 6, None])
        self.assertEqual(self.solve(tree), [1, 3, 6])

    def test_repeated_values_are_all_reported(self):
        # The view holds values, not node identities, so equal values repeat.
        tree = build([0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(self.solve(tree), [0, 0, 0])
        tree = build([-1, -1, -1, None, -1])
        self.assertEqual(self.solve(tree), [-1, -1, -1])

    def test_negative_and_boundary_values(self):
        # Two levels: the root's right child is the visible node.
        tree = build([-100, -100, 100])
        self.assertEqual(self.solve(tree), [-100, 100])
        self.assertEqual(self.assert_view(tree), [-100, 100])
        # Three levels: the deepest visible node hangs off the left child.
        tree = build([-100, -100, 100, None, 100])
        self.assertEqual(self.solve(tree), [-100, 100, 100])
        self.assertEqual(self.assert_view(tree), [-100, 100, 100])
        tree = build([100] * 7)
        self.assertEqual(self.solve(tree), [100, 100, 100])

    def test_exhaustive_shapes_with_up_to_six_nodes(self):
        total = 0
        for size in range(1, 7):
            for shape in shapes(size):
                tree = fill(shape, range(1, size + 1))
                with self.subTest(size=size, shape=shape):
                    self.assert_view(tree)
                total += 1
        # Catalan(1..6) = 1 + 2 + 5 + 14 + 42 + 132
        self.assertEqual(total, 196)

    def test_exhaustive_shapes_with_a_second_value_assignment(self):
        for size in range(1, 6):
            for shape in shapes(size):
                tree = fill(shape, range(size, 0, -1))
                with self.subTest(size=size, shape=shape):
                    self.assert_view(tree)
                tree = fill(shape, [7] * size)
                with self.subTest(size=size, shape=shape, equal=True):
                    self.assertEqual(self.solve(tree), [7] * height(tree))

    def test_randomised_trees(self):
        rng = random.Random(1990)
        for _ in range(400):
            size = rng.randint(0, 40)
            values = [rng.randint(-100, 100) for _ in range(size)]
            tree = build(values)
            with self.subTest(values=values):
                self.assert_view(tree)

    def test_randomised_left_leaning_trees(self):
        # Shapes where many levels contain a single left child.
        rng = random.Random(1991)
        for _ in range(200):
            size = rng.randint(1, 30)
            values = [rng.randint(-100, 100) for _ in range(size)]
            slots = []
            for index in range(size):
                slots.append(values[index])
                if rng.random() < 0.7:
                    slots.append(None)
            tree = build(slots)
            with self.subTest(values=slots):
                self.assert_view(tree)

    def test_constraint_sized(self):
        # 100 nodes is the constraint maximum, in shapes that stress the level
        # width and the level count respectively.
        complete = build(list(range(100)))
        self.assertEqual(len(nodes(complete)), 100)
        self.assertEqual(self.assert_view(complete), [0, 2, 6, 14, 30, 62, 99])

        left_spine = [1]
        for value in range(2, 101):
            left_spine += [value, None]
        tree = build(left_spine)
        self.assertEqual(len(nodes(tree)), 100)
        self.assertEqual(height(tree), 100)
        self.assertEqual(self.solve(tree), list(range(1, 101)))
        self.assertEqual(self.assert_view(tree), list(range(1, 101)))

        right_spine = [1]
        for value in range(2, 101):
            right_spine += [None, value]
        tree = build(right_spine)
        self.assertEqual(len(nodes(tree)), 100)
        self.assertEqual(self.solve(tree), list(range(1, 101)))

    def test_constraint_sized_random(self):
        rng = random.Random(1992)
        for case in range(20):
            values = [rng.randint(-100, 100) for _ in range(100)]
            tree = build(values)
            with self.subTest(case=case):
                self.assertEqual(len(nodes(tree)), 100)
                self.assert_view(tree)


if __name__ == '__main__':
    unittest.main()
