"""Tests for 129. Sum Root to Leaf Numbers.

Three ways to get the expected total, none of which uses the solution's
"value * 10 + digit" recurrence:

  - `path_sum_by_strings` collects each root-to-leaf path as a list of digits and
    parses it with `int(''.join(...))`;
  - `path_sum_by_powers` rebuilds each number as a weighted sum of powers of ten;
  - `complete_tree_closed_form` computes the constraint-sized case straight from
    the level-order array: in that fixture every node above the last two levels
    holds 0, so a leaf at level 8 contributes its own digit and a leaf at level 9
    contributes 10 * parent_digit + its own digit -- no traversal at all.

The exhaustive sweep pairs every tree shape with up to four nodes against every
assignment of digits from {0, 1, 9}, which is where leading zeros and one-child
nodes appear.
"""

import itertools
import random
import unittest

from _loader import load_solution
from _trees import build, from_structure

Solution = load_solution('129-sum-root-to-leaf-numbers.py').Solution


def leaf_paths(root) -> list:
    """Every root-to-leaf path, as a list of the node values on it."""
    paths = []

    def walk(node, path):
        if node is None:
            return
        path = path + [node.val]
        if node.left is None and node.right is None:
            paths.append(path)
            return
        walk(node.left, path)
        walk(node.right, path)

    walk(root, [])
    return paths


def path_sum_by_strings(root) -> int:
    return sum(int(''.join(str(digit) for digit in path)) for path in leaf_paths(root))


def path_sum_by_powers(root) -> int:
    total = 0
    for path in leaf_paths(root):
        number = 0
        for offset, digit in enumerate(path):
            number += digit * 10 ** (len(path) - 1 - offset)
        total += number
    return total


def shapes(size: int) -> list:
    """All binary-tree shapes with `size` nodes, as (left, right) tuples."""
    if size == 0:
        return [None]
    result = []
    for left_size in range(size):
        for left in shapes(left_size):
            for right in shapes(size - 1 - left_size):
                result.append((left, right))
    return result


def fill(shape, digits) -> "TreeNode | None":
    """Build a tree from a shape and a pre-order sequence of node values."""
    iterator = iter(digits)

    def convert(node):
        if node is None:
            return None
        value = next(iterator)
        return (value, convert(node[0]), convert(node[1]))

    return from_structure(convert(shape))


def left_chain(depth: int) -> "TreeNode | None":
    """A single left spine of `depth` nodes, each holding the value 1."""
    structure = None
    for _ in range(depth):
        structure = (1, structure, None)
    return from_structure(structure)


def random_shape(rng, size: int, depth_limit: int):
    """Random shape with `size` nodes that never exceeds `depth_limit` levels."""
    def node(remaining: int, depth_left: int):
        if remaining == 0 or depth_left == 0:
            return None
        left_size = rng.randint(0, remaining - 1)
        return (node(left_size, depth_left - 1), node(remaining - 1 - left_size, depth_left - 1))

    return node(size, depth_limit)


def complete_tree_values(count: int, rng) -> list:
    """Level-order values of a complete binary tree: zeros high up, digits low."""
    values = []
    for index in range(count):
        level = index.bit_length()  # 1-based level of a complete tree
        values.append(0 if level <= 8 else rng.randint(0, 9))
    return values


def complete_tree_closed_form(values: list) -> int:
    """Total for the fixture above, read straight from the level-order array."""
    count = len(values)
    total = 0
    for index in range(count):
        left, right = 2 * index + 1, 2 * index + 2
        if left < count or right < count:
            continue  # not a leaf
        depth = index.bit_length()
        if depth == 9:
            total += values[index]  # every ancestor holds 0
        else:
            total += 10 * values[(index - 1) // 2] + values[index]
    return total


class SumRootToLeafNumbersTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().sumNumbers

    def test_official_examples(self):
        self.assertEqual(self.solve(build([1, 2, 3])), 25)
        self.assertEqual(self.solve(build([4, 9, 0, 5, 1])), 1026)

    def test_single_node(self):
        for value in range(10):
            with self.subTest(value=value):
                self.assertEqual(self.solve(build([value])), value)

    def test_chains(self):
        # Level-order lists: a null consumes a slot without creating a node.
        self.assertEqual(self.solve(build([1, 2, 3])), 12 + 13)
        self.assertEqual(self.solve(build([1, 2, None, 3])), 123)
        self.assertEqual(self.solve(build([1, 2, None, 3, None, 4, None])), 1234)
        self.assertEqual(self.solve(build([1, None, 2, None, 3])), 123)
        self.assertEqual(self.solve(build([9, 8, None, 7])), 987)
        self.assertEqual(self.solve(build([9, None, 8, None, 7])), 987)

    def test_leading_zero_paths(self):
        self.assertEqual(self.solve(build([0, 0])), 0)
        self.assertEqual(self.solve(build([0, 1])), 1)
        self.assertEqual(self.solve(build([0, 1, None, 2])), 12)
        self.assertEqual(self.solve(build([0, 1, 2])), 1 + 2)
        self.assertEqual(self.solve(build([0, 0, 1])), 1)
        self.assertEqual(self.solve(build([0, 0, 0, 7])), 7)
        self.assertEqual(self.solve(build([1, 0, 1])), 10 + 11)

    def test_one_child_nodes_are_not_leaves(self):
        # A node with a single child is not a leaf, so it must not be counted.
        self.assertEqual(self.solve(build([1, 2])), 12)
        self.assertEqual(self.solve(build([1, None, 2])), 12)
        self.assertEqual(self.solve(build([1, 2, None, 3])), 123)
        self.assertEqual(self.solve(build([1, None, 2, None, 3])), 123)

    def test_all_equal_digits(self):
        # Seven nodes in level order: a root, two children and four leaves.
        self.assertEqual(self.solve(build([7, 7, 7])), 77 + 77)
        self.assertEqual(self.solve(build([9] * 7)), 4 * (10 ** 3 - 1))
        self.assertEqual(self.solve(build([1] * 7)), 4 * 111)

    def test_exhaustive_shapes_and_digits(self):
        for size in range(1, 5):
            for shape in shapes(size):
                for digits in itertools.product((0, 1, 9), repeat=size):
                    tree = fill(shape, digits)
                    with self.subTest(size=size, digits=digits):
                        expected = path_sum_by_strings(tree)
                        self.assertEqual(self.solve(tree), expected)
                        self.assertEqual(expected, path_sum_by_powers(tree))

    def test_exhaustive_small_shapes_all_digits(self):
        for size in range(1, 4):
            for shape in shapes(size):
                for digits in itertools.product(range(10), repeat=size):
                    tree = fill(shape, digits)
                    with self.subTest(size=size, digits=digits):
                        self.assertEqual(self.solve(tree), path_sum_by_strings(tree))

    def test_randomised_trees(self):
        rng = random.Random(1290)
        for _ in range(300):
            size = rng.randint(1, 40)
            shape = random_shape(rng, size, 10)
            digits = [rng.randint(0, 9) for _ in range(size)]
            tree = fill(shape, digits)
            with self.subTest(size=size, digits=digits):
                expected = path_sum_by_strings(tree)
                self.assertEqual(self.solve(tree), expected)
                self.assertEqual(expected, path_sum_by_powers(tree))

    def test_randomised_level_order_trees(self):
        rng = random.Random(1291)
        for _ in range(200):
            size = rng.randint(1, 60)
            values = [rng.randint(0, 9) for _ in range(size)]
            tree = build(values)
            with self.subTest(values=values):
                self.assertEqual(self.solve(tree), path_sum_by_strings(tree))

    def test_randomised_trees_with_holes(self):
        rng = random.Random(1292)
        for _ in range(200):
            size = rng.randint(2, 40)
            values = [rng.choice((0, 1, 5, 9, None)) for _ in range(size)]
            values[0] = rng.randint(0, 9)
            tree = build(values)
            with self.subTest(values=values):
                self.assertEqual(self.solve(tree), path_sum_by_strings(tree))

    def test_constraint_sized_complete_tree(self):
        # 1000 nodes, exactly the depth limit of 10, and the answer is small
        # enough to fit a 32-bit integer because the upper levels are all 0.
        rng = random.Random(1293)
        values = complete_tree_values(1000, rng)
        tree = build(values)

        expected = complete_tree_closed_form(values)
        self.assertEqual(self.solve(tree), expected)
        self.assertEqual(self.solve(tree), path_sum_by_strings(tree))
        self.assertEqual(self.solve(tree), path_sum_by_powers(tree))
        self.assertEqual(len([path for path in leaf_paths(tree)]), 500)
        self.assertLess(expected, 2 ** 31)

    def test_constraint_sized_deep_chain(self):
        # Depth 10, the allowed maximum, and 1111111111 < 2^31. A chain has to be
        # written as nested structures: a level-order list of ten ones would be a
        # complete tree instead.
        tree = left_chain(10)
        self.assertEqual(self.solve(tree), 1111111111)
        self.assertEqual(self.solve(tree), path_sum_by_strings(tree))
        self.assertEqual(self.solve(left_chain(9)), 111111111)

    def test_complete_tree_of_ten_nodes(self):
        # Levels 1..3 hold four nodes, level 4 holds six; the leaves are the two
        # level-3 nodes and the three level-4 nodes.
        tree = build([1] * 10)
        self.assertEqual(self.solve(tree), 2 * 111 + 3 * 1111)
        self.assertEqual(self.solve(tree), path_sum_by_strings(tree))

    def test_constraint_sized_wide_and_flat(self):
        self.assertEqual(self.solve(build([0] * 1000)), 0)
        # Only the last leaf holds a digit, and every ancestor of it is 0.
        tree = build([0] * 999 + [7])
        self.assertEqual(self.solve(tree), 7)
        self.assertEqual(self.solve(tree), path_sum_by_strings(tree))


if __name__ == '__main__':
    unittest.main()
