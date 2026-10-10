"""Tests for 124. Binary Tree Maximum Path Sum.

Oracles:
  - ``brute_force``: the path between two nodes in a tree is unique, so summing
    over every ordered pair of nodes and taking the best covers every path
    literally. Pairs are resolved through their lowest common ancestor.
  - ``diameter_value``: when every value is the same v > 0 the best path is the
    longest one, so the answer is v times the number of nodes on a diameter,
    measured by two BFS passes. No sum DP involved.
  - ``kadane``: a right-leaning chain is a list, and the best path there is the
    maximum non-empty subarray sum.
  - ``max_node``: with every value negative, a single node always beats any
    longer path, so the answer is the largest value.

Exhaustive sweep: every tree shape with up to four nodes over {-3, -1, 0, 2} and
every shape with five or six nodes over {-2, 3}, plus random trees against the
pair enumeration. The 3 * 10^4-node cases use the chain, diameter and
all-negative closed forms.
"""

import collections
import itertools
import random
import unittest

from _loader import load_solution
from _trees import TreeNode, build, from_structure, serialize

Solution = load_solution('124-binary-tree-maximum-path-sum.py').Solution

MAX_NODES = 3 * 10 ** 4
MAX_VALUE = 1000


def upward_paths(root) -> dict:
    """node -> [node, ..., root], so common ancestors sit at the list ends."""
    paths = {}

    def walk(node, ancestors):
        if node is None:
            return
        here = [node] + ancestors
        paths[node] = here
        walk(node.left, here)
        walk(node.right, here)

    walk(root, [])
    return paths


def brute_force(root):
    """Best sum over every ordered node pair; a path is fixed by its two ends."""
    if root is None:
        return None
    paths = upward_paths(root)
    best = None
    for start in paths.values():
        for end in paths.values():
            i, j = len(start) - 1, len(end) - 1
            while i >= 0 and j >= 0 and start[i] is end[j]:
                i -= 1
                j -= 1
            total = sum(node.val for node in start[:i + 1])
            total += sum(node.val for node in end[:j + 1])
            total += start[i + 1].val
            if best is None or total > best:
                best = total
    return best


def kadane(values) -> int:
    """Maximum non-empty subarray sum."""
    best = current = values[0]
    for value in values[1:]:
        current = max(value, current + value)
        best = max(best, current)
    return best


def diameter_nodes(root) -> int:
    """Number of nodes on a longest path, found with two BFS passes.

    A diameter search has to cross edges in both directions, so the tree is
    first turned into an undirected adjacency map; a downward-only walk would
    never come back up from a leaf.
    """
    if root is None:
        return 0

    neighbours = {root: []}
    stack = [root]
    while stack:
        node = stack.pop()
        for child in (node.left, node.right):
            if child is not None:
                neighbours[node].append(child)
                neighbours.setdefault(child, []).append(node)
                stack.append(child)

    def farthest(start):
        distances = {start: 0}
        queue = collections.deque([start])
        last = start
        while queue:
            node = queue.popleft()
            last = node
            for other in neighbours[node]:
                if other not in distances:
                    distances[other] = distances[node] + 1
                    queue.append(other)
        return last, distances[last]

    end, _ = farthest(root)
    _, distance = farthest(end)
    return distance + 1


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
    """Place `values` over a shape in pre-order, matching (val, left, right)."""
    iterator = iter(values)

    def place(node):
        if node is None:
            return None
        left, right = node
        return (next(iterator), place(left), place(right))

    return place(shape)


def random_tree(rng, size, values) -> "TreeNode | None":
    """A random tree with exactly `size` nodes, round-tripped through the helpers."""
    if size <= 0:
        return None
    root = TreeNode(rng.choice(values))
    created = [root]
    free = [root]
    while len(created) < size:
        index = rng.randrange(len(free))
        node = free[index]
        if node.left is None and node.right is None:
            side = 'left' if rng.random() < 0.5 else 'right'
        elif node.left is None:
            side = 'left'
        else:
            side = 'right'
        child = TreeNode(rng.choice(values))
        setattr(node, side, child)
        created.append(child)
        if node.left is not None and node.right is not None:
            free[index] = free[-1]
            free.pop()
        free.append(child)
    return build(serialize(root))


def chain_level_order(values) -> list:
    """Level-order list for a tree that only has right children."""
    order = []
    for value in values:
        order.append(value)
        order.append(None)
    order.pop()
    return order


class BinaryTreeMaximumPathSumTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().maxPathSum

    def test_official_examples(self):
        self.assertEqual(self.solve(build([1, 2, 3])), 6)
        self.assertEqual(self.solve(build([-10, 9, 20, None, None, 15, 7])), 42)

    def test_single_node(self):
        for value in (-MAX_VALUE, -1, 0, 1, MAX_VALUE):
            with self.subTest(value=value):
                self.assertEqual(self.solve(TreeNode(value)), value)

    def test_path_need_not_pass_through_the_root(self):
        # The best path sits entirely inside the right subtree.
        self.assertEqual(self.solve(build([-10, 9, 20, None, None, 15, 7])), 42)
        self.assertEqual(self.solve(build([1, -5, 4, None, None, 3, 2])), 9)

    def test_unprofitable_branches_are_clipped(self):
        # 2 -> 1 -> 3 is worth 6, so the 2 is kept; 1 -> 3 alone is worth 4.
        self.assertEqual(self.solve(build([1, 2, 3])), 6)
        self.assertEqual(self.solve(build([1, -2, 3])), 4)
        # A very negative branch is dropped rather than dragged along.
        self.assertEqual(self.solve(build([2, -100, 3])), 5)
        self.assertEqual(self.solve(build([2, -100, 3])), brute_force(build([2, -100, 3])))

    def test_all_negative_values(self):
        cases = [
            [-1],
            [-3, -2, -1],
            [-5, -4, None, -6, -7],
            [-1000, -999, -998, -1000, -1000],
            [-1, -2, None, -3, None, -4],
        ]
        for values in cases:
            root = build(values)
            with self.subTest(values=values):
                self.assertEqual(self.solve(root), max(node.val for node in upward_paths(root)))
                self.assertEqual(self.solve(root), brute_force(root))

    def test_exhaustive_small_shapes(self):
        for size in range(1, 5):
            for shape in all_shapes(size):
                for values in itertools.product((-3, -1, 0, 2), repeat=size):
                    with self.subTest(size=size, values=values):
                        root = from_structure(fill(shape, values))
                        self.assertEqual(self.solve(root), brute_force(root))
        for size in (5, 6):
            for shape in all_shapes(size):
                for values in itertools.product((-2, 3), repeat=size):
                    with self.subTest(size=size, values=values):
                        root = from_structure(fill(shape, values))
                        self.assertEqual(self.solve(root), brute_force(root))

    def test_random_trees_against_the_pair_enumeration(self):
        rng = random.Random(1240)
        for _ in range(600):
            size = rng.randint(1, 14)
            root = random_tree(rng, size, list(range(-10, 11)))
            with self.subTest(size=size):
                self.assertEqual(self.solve(root), brute_force(root))

    def test_medium_random_trees(self):
        rng = random.Random(1241)
        for _ in range(10):
            size = rng.randint(40, 80)
            root = random_tree(rng, size, list(range(-1000, 1001)))
            with self.subTest(size=size):
                self.assertEqual(self.solve(root), brute_force(root))

    def test_constraint_sized_chain_against_kadane(self):
        rng = random.Random(1242)
        values = [rng.randint(-MAX_VALUE, MAX_VALUE) for _ in range(MAX_NODES)]
        root = build(chain_level_order(values))
        self.assertEqual(len(serialize(root)), 2 * MAX_NODES - 1)
        # A right-leaning chain is a list, so the best path is a subarray.
        self.assertEqual(self.solve(root), kadane(values))
        self.assertEqual(self.solve(build(chain_level_order([MAX_VALUE] * MAX_NODES))),
                         MAX_VALUE * MAX_NODES)
        self.assertEqual(self.solve(build(chain_level_order([-1] * MAX_NODES))), -1)
        # The best subarray of a random walk is neither the whole chain nor a
        # single node, so the case really exercises the tie-breaking.
        self.assertGreater(self.solve(root), max(values))
        self.assertLess(self.solve(root), sum(v for v in values if v > 0))

    def test_constraint_sized_uniform_trees(self):
        rng = random.Random(1243)
        root = random_tree(rng, MAX_NODES, [7])
        longest = diameter_nodes(root)
        self.assertEqual(self.solve(root), 7 * longest)
        self.assertGreater(longest, 1)

        negative = random_tree(rng, MAX_NODES, [-3])
        self.assertEqual(self.solve(negative), -3)

        # A mixed-sign tree: the answer is sandwiched between the best single
        # node and the total of the positive values, and any path is a set of
        # distinct nodes, so both bounds are structural.
        mixed = random_tree(rng, MAX_NODES, list(range(-MAX_VALUE, MAX_VALUE + 1)))
        values = []
        stack = [mixed]
        while stack:
            node = stack.pop()
            values.append(node.val)
            for child in (node.left, node.right):
                if child is not None:
                    stack.append(child)
        self.assertEqual(len(values), MAX_NODES)
        answer = self.solve(mixed)
        self.assertLessEqual(answer, sum(value for value in values if value > 0))
        self.assertGreaterEqual(answer, max(values))


if __name__ == '__main__':
    unittest.main()
