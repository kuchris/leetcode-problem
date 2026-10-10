"""Tests for 113. Path Sum II.

Oracle: collect every root-to-leaf path as an explicit list by plain recursion,
then keep the ones whose sum matches. It materialises all paths instead of
tracking remaining sums, so it is a different program from the solution's
stack-based DFS, and it exposes the same two traps as problem 112: an empty tree
has no paths, and a matching prefix that stops at a non-leaf does not count.

Results are order-insensitive on LeetCode, so comparisons sort the paths.
"""

import itertools
import random
import unittest

from _loader import load_solution
from _trees import TreeNode, build, from_structure

Solution = load_solution('113-path-sum-ii.py').Solution


def all_paths(node, prefix=None) -> list:
    if node is None:
        return []
    path = (prefix if prefix is not None else []) + [node.val]
    if node.left is None and node.right is None:
        return [path]
    return all_paths(node.left, path) + all_paths(node.right, path)


def oracle(root, target: int) -> list:
    return sorted(tuple(path) for path in all_paths(root) if sum(path) == target)


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
    values = []
    for _ in range(size):
        values.append(value)
        values.append(None)
    values.pop()
    return values


class PathSumIITests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().pathSum

    def result(self, root, target):
        return sorted(tuple(path) for path in self.solve(root, target))

    def check(self, values, target):
        root = build(values)
        produced = self.result(root, target)
        self.assertEqual(produced, oracle(root, target))
        # Every returned path must be a real root-to-leaf path.
        valid = {tuple(path) for path in all_paths(root)}
        for path in produced:
            self.assertIn(path, valid)
        return produced

    def test_official_examples(self):
        self.assertEqual(
            self.check([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1], 22),
            [(5, 4, 11, 2), (5, 8, 4, 5)],
        )
        self.assertEqual(self.check([1, 2, 3], 5), [])
        self.assertEqual(self.check([1, 2], 0), [])

    def test_empty_tree(self):
        self.assertEqual(self.solve(None, 0), [])
        self.assertEqual(self.solve(None, -1000), [])

    def test_single_node(self):
        self.assertEqual(self.check([7], 7), [(7,)])
        self.assertEqual(self.check([7], 0), [])
        self.assertEqual(self.check([-1000], -1000), [(-1000,)])

    def test_path_must_end_at_a_leaf(self):
        self.assertEqual(self.check([1, 2], 1), [])
        self.assertEqual(self.check([1, 2], 3), [(1, 2)])
        self.assertEqual(self.check([1, 2, None, 3], 3), [])
        self.assertEqual(self.check([1, 2, None, 3], 6), [(1, 2, 3)])

    def test_zero_and_negative_values(self):
        self.assertEqual(self.check([0, 0, 0], 0), [(0, 0), (0, 0)])
        self.assertEqual(self.check([1, -1, 0], 0), [(1, -1)])
        self.assertEqual(self.check([-2, None, -3], -5), [(-2, -3)])

    def test_duplicate_paths_are_all_listed(self):
        # Two leaves, both reached by the value sequence 1, 1.
        self.assertEqual(self.check([1, 1, 1], 2), [(1, 1), (1, 1)])
        # Two leaves, two identical three-value paths.
        self.assertEqual(self.check([1, 1, 1, 1, None, 1, None], 3),
                         [(1, 1, 1), (1, 1, 1)])
        self.assertEqual(self.check([1, 1, 1, 1, None, 1, None], 2), [])

    def test_exhaustive_small_cases(self):
        targets = (-2, -1, 0, 1, 2)
        for size in range(0, 5):
            for shape in all_shapes(size):
                for values in itertools.product((-1, 0, 1), repeat=size):
                    root = from_structure(fill(shape, values))
                    for target in targets:
                        with self.subTest(size=size, values=values, target=target):
                            self.assertEqual(self.result(root, target),
                                             oracle(root, target))
        for shape in all_shapes(5):
            for values in itertools.product((0, 1), repeat=5):
                root = from_structure(fill(shape, values))
                for target in targets:
                    with self.subTest(size=5, values=values, target=target):
                        self.assertEqual(self.result(root, target),
                                         oracle(root, target))

    def test_random_cases(self):
        rng = random.Random(1130)
        for _ in range(300):
            size = rng.randint(0, 120)
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
                self.assertEqual(self.result(root, target), oracle(root, target))

    def test_random_matching_targets(self):
        rng = random.Random(1131)
        for _ in range(200):
            size = rng.randint(1, 50)
            root = build(list(rng.randint(-3, 3) for _ in range(size)))
            paths = all_paths(root)
            target = sum(rng.choice(paths))
            with self.subTest(size=size, target=target):
                produced = self.result(root, target)
                self.assertTrue(produced)
                self.assertEqual(produced, oracle(root, target))

    def test_constraint_sized(self):
        # 5000 nodes is the constraint maximum.
        chain = build(chained(5000))
        self.assertEqual(self.solve(chain, 0), [[0] * 5000])
        self.assertEqual(self.solve(chain, 1), [])

        # A perfect tree of 4095 nodes of value 1 has 2048 leaves; every
        # root-to-leaf path has 12 nodes.
        complete = build([1] * 4095)
        produced = self.solve(complete, 12)
        self.assertEqual(len(produced), 2048)
        self.assertTrue(all(len(path) == 12 for path in produced))
        self.assertEqual(self.result(complete, 12), oracle(complete, 12))
        self.assertEqual(self.solve(complete, 13), [])

        # All-zero perfect tree: every one of the 2048 paths sums to 0.
        zeros = build([0] * 4095)
        self.assertEqual(len(self.solve(zeros, 0)), 2048)
        self.assertEqual(len(self.solve(zeros, 1)), 0)


if __name__ == '__main__':
    unittest.main()
