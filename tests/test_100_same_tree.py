"""Tests for 100. Same Tree.

Oracle: encode both trees as nested ``(value, left, right)`` tuples with
``to_structure`` and compare the encodings. That is a pure data comparison with
no traversal control flow, so it is independent of the solution's simultaneous
walk.

Exhaustive sweep: every ordered pair of trees with up to four nodes over the
value alphabet {0, 1}, including the empty tree.
"""

import itertools
import random
import unittest

from _loader import load_solution
from _trees import TreeNode, build, from_structure, to_structure

Solution = load_solution('100-same-tree.py').Solution


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


def all_small_trees(max_size=4, alphabet=(0, 1)):
    """Every tree with at most `max_size` nodes over `alphabet`, as structures."""
    trees = [None]
    for size in range(1, max_size + 1):
        for shape in all_shapes(size):
            for values in itertools.product(alphabet, repeat=size):
                trees.append(fill(shape, values))
    return trees


def chained(size: int, start: int = 1) -> "TreeNode | None":
    """A right-leaning chain of `size` nodes with consecutive values."""
    root = None
    for value in reversed(range(start, start + size)):
        root = TreeNode(value, None, root)
    return root


def left_chained(size: int, start: int = 1) -> "TreeNode | None":
    """A left-leaning chain of `size` nodes with consecutive values."""
    root = None
    for value in range(start, start + size):
        root = TreeNode(value, root, None)
    return root


class SameTreeTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().isSameTree

    def check(self, p_values, q_values):
        return self.solve(build(p_values), build(q_values))

    def test_official_examples(self):
        self.assertTrue(self.check([1, 2, 3], [1, 2, 3]))
        self.assertFalse(self.check([1, 2], [1, None, 2]))
        self.assertFalse(self.check([1, 2, 1], [1, 1, 2]))

    def test_empty_trees(self):
        self.assertTrue(self.solve(None, None))
        self.assertFalse(self.solve(None, build([1])))
        self.assertFalse(self.solve(build([1]), None))
        self.assertTrue(self.check([], []))

    def test_single_and_two_nodes(self):
        self.assertTrue(self.check([1], [1]))
        self.assertFalse(self.check([1], [2]))
        self.assertTrue(self.check([1, 2], [1, 2]))
        self.assertFalse(self.check([1, 2], [1, None, 2]))
        self.assertFalse(self.check([1, 2], [1, 3]))
        self.assertTrue(self.check([1, None, 2], [1, None, 2]))

    def test_structure_versus_values(self):
        # Same values, different shapes.
        self.assertFalse(self.check([1, 2, None], [1, None, 2]))
        self.assertFalse(self.check([2, 1, 3], [2, 1, None, 3]))
        # Same shape and values, deeper.
        self.assertTrue(self.check([2, 1, 3, None, None, 4], [2, 1, 3, None, None, 4]))
        # One deep value differs.
        self.assertFalse(self.check([2, 1, 3, None, None, 4], [2, 1, 3, None, None, 5]))

    def test_boundary_values(self):
        self.assertTrue(self.check([0, -10_000, 10_000], [0, -10_000, 10_000]))
        self.assertFalse(self.check([0, -10_000], [0, -9_999]))

    def test_left_and_right_are_distinguished(self):
        self.assertFalse(self.check([1, 2, None], [1, None, 2]))
        self.assertFalse(self.check([1, 2, 3], [1, 3, 2]))
        self.assertTrue(self.check([1, 2, 3], [1, 2, 3]))

    def test_exhaustive_all_pairs_of_small_trees(self):
        trees = all_small_trees()
        self.assertEqual(len(trees), 275)  # 1 + 2 + 8 + 40 + 224
        built = [(structure, from_structure(structure)) for structure in trees]
        for p_structure, p in built:
            for q_structure, q in built:
                with self.subTest(p=p_structure, q=q_structure):
                    self.assertEqual(
                        self.solve(p, q),
                        to_structure(p) == to_structure(q),
                    )

    def test_random_trees(self):
        rng = random.Random(1000)
        for _ in range(400):
            size = rng.randint(0, 30)
            p_values = []
            q_values = []
            if size:
                p_values.append(rng.randint(-10_000, 10_000))
                q_values.append(rng.randint(-10_000, 10_000))
                p_values.extend(
                    None if rng.random() < 0.3 else rng.randint(-10_000, 10_000)
                    for _ in range(size - 1)
                )
                # q is either a copy of p (with one mutation) or unrelated.
                if rng.random() < 0.5:
                    q_values = list(p_values)
                    if rng.random() < 0.5 and q_values:
                        index = rng.randrange(len(q_values))
                        if q_values[index] is None:
                            q_values[index] = rng.randint(-2, 2)
                        else:
                            q_values[index] = None if rng.random() < 0.5 \
                                else q_values[index] + rng.choice([-1, 1])
                else:
                    q_values.extend(
                        None if rng.random() < 0.3 else rng.randint(-10_000, 10_000)
                        for _ in range(size - 1)
                    )
            p = build(p_values)
            q = build(q_values)
            with self.subTest(size=size, p=p_values, q=q_values):
                self.assertEqual(self.solve(p, q), to_structure(p) == to_structure(q))

    def test_random_equal_copies(self):
        rng = random.Random(1001)
        for _ in range(200):
            size = rng.randint(1, 40)
            values = [rng.randint(-100, 100)]
            values.extend(
                None if rng.random() < 0.3 else rng.randint(-100, 100)
                for _ in range(size - 1)
            )
            p = build(values)
            with self.subTest(values=values):
                # Identical inputs are equal by construction.
                self.assertTrue(self.solve(p, build(list(values))))
                # Mirroring the root's two child slots changes the tree whenever
                # the two child values differ.
                if len(values) >= 3 and values[1] != values[2]:
                    mirrored = list(values)
                    mirrored[1], mirrored[2] = mirrored[2], mirrored[1]
                    self.assertFalse(self.solve(p, build(mirrored)))

    def test_constraint_sized(self):
        # 100 nodes is the constraint maximum for each tree.
        self.assertTrue(self.solve(chained(100), chained(100)))
        self.assertTrue(self.solve(chained(100, -50), chained(100, -50)))
        self.assertFalse(self.solve(chained(100), chained(100, 2)))
        # Same length, one different value at the far end.
        other = chained(100)
        node = other
        while node.right is not None:
            node = node.right
        node.val = 0
        self.assertFalse(self.solve(chained(100), other))
        # An extra node makes the structures differ.
        self.assertFalse(self.solve(chained(100), TreeNode(0, None, chained(100))))
        # A left chain against a right chain of the same values.
        self.assertFalse(self.solve(left_chained(100), chained(100)))
        self.assertTrue(self.solve(left_chained(100), left_chained(100)))

        # Balanced trees of 100 nodes, equal and with one deep difference.
        def balanced(values):
            if not values:
                return None
            middle = len(values) // 2
            return TreeNode(values[middle], balanced(values[:middle]),
                            balanced(values[middle + 1:]))

        self.assertTrue(self.solve(balanced(list(range(100))), balanced(list(range(100)))))
        broken = list(range(100))
        broken[99] = -1
        self.assertFalse(self.solve(balanced(list(range(100))), balanced(broken)))


if __name__ == '__main__':
    unittest.main()
