"""Tests for 101. Symmetric Tree.

Two oracles, both independent of the stack walk under test:

  - structural: a tree is symmetric exactly when its nested-tuple structure
    equals its own mirror, so the check is an equality between two data
    structures rather than a traversal comparison;
  - positional: label each node with (depth, index inside its level) using the
    heap convention (left child 2x, right child 2x + 1) and require every
    occupied slot to match its mirror slot 2^depth - 1 - x. That is pure
    geometry -- it never walks the tree in any traversal order.

The positional oracle is iterative, which is what makes the deep
constraint-sized chains checkable at all.
"""

import random
import unittest

from _loader import load_solution
from _trees import TreeNode, from_structure, serialize, to_structure

module = load_solution('101-symmetric-tree.py')
Solution = module.Solution


def mirror(structure):
    """Mirror a nested (value, left, right) structure."""
    if structure is None:
        return None
    value, left, right = structure
    return (value, mirror(right), mirror(left))


def structural_oracle(root) -> bool:
    structure = to_structure(root)
    return structure == mirror(structure)


def positional(root) -> dict:
    """{depth: {index_in_level: value}} with the heap index convention."""
    levels: dict = {}
    if root is None:
        return levels
    level = [(root, 0)]
    depth = 0
    while level:
        levels[depth] = {index: node.val for node, index in level}
        following = []
        for node, index in level:
            if node.left is not None:
                following.append((node.left, 2 * index))
            if node.right is not None:
                following.append((node.right, 2 * index + 1))
        level = following
        depth += 1
    return levels


def positional_oracle(root) -> bool:
    for depth, slots in positional(root).items():
        width = 1 << depth
        for index, value in slots.items():
            if slots.get(width - 1 - index) != value:
                return False
    return True


def shapes(size: int) -> list:
    """Every binary tree shape with `size` nodes, as (left, right) pairs."""
    if size == 0:
        return [None]
    out = []
    for left_size in range(size):
        for left in shapes(left_size):
            for right in shapes(size - 1 - left_size):
                out.append((left, right))
    return out


def fill_preorder(shape, values):
    """Assign values to a shape in pre-order sequence."""
    iterator = iter(values)

    def walk(node):
        if node is None:
            return None
        value = next(iterator)
        return (value, walk(node[0]), walk(node[1]))

    return walk(shape)


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


def mirror_tree(root) -> "TreeNode | None":
    """Iterative mirror clone of a tree."""
    if root is None:
        return None
    clone = TreeNode(root.val)
    stack = [(root, clone)]
    while stack:
        source, target = stack.pop()
        if source.left is not None:
            target.right = TreeNode(source.left.val)
            stack.append((source.left, target.right))
        if source.right is not None:
            target.left = TreeNode(source.right.val)
            stack.append((source.right, target.left))
    return clone


def chain(size: int, to_the_left: bool, value: int = 0) -> TreeNode:
    """A chain of `size` nodes, built iteratively (the deepest shape)."""
    root = None
    for _ in range(size):
        root = TreeNode(value, root, None) if to_the_left else TreeNode(value, None, root)
    return root


def complete_tree(size: int, offset: int = 0) -> TreeNode:
    """A complete tree with `size` nodes built level by level, iteratively."""
    root = TreeNode((offset + 0) % 201 - 100)
    queue = [root]
    created = 1
    while created < size:
        node = queue.pop(0)
        node.left = TreeNode((offset + created) % 201 - 100)
        created += 1
        queue.append(node.left)
        if created < size:
            node.right = TreeNode((offset + created) % 201 - 100)
            created += 1
            queue.append(node.right)
    return root


def node_count(root) -> int:
    count = 0
    stack = [root] if root is not None else []
    while stack:
        node = stack.pop()
        count += 1
        if node.left is not None:
            stack.append(node.left)
        if node.right is not None:
            stack.append(node.right)
    return count


class SymmetricTreeTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().isSymmetric

    def check(self, root, expected):
        self.assertEqual(self.solve(root), expected)
        self.assertEqual(structural_oracle(root), expected)
        self.assertEqual(positional_oracle(root), expected)

    def test_official_examples(self):
        self.check(from_structure((1, (2, (3, None, None), (4, None, None)),
                                   (2, (4, None, None), (3, None, None)))), True)
        self.check(from_structure((1, (2, None, (3, None, None)),
                                   (2, None, (3, None, None)))), False)

    def test_empty_tree(self):
        self.assertTrue(self.solve(None))

    def test_single_node(self):
        self.check(from_structure((1, None, None)), True)
        self.check(from_structure((-100, None, None)), True)

    def test_one_child_is_never_symmetric(self):
        self.check(from_structure((1, (2, None, None), None)), False)
        self.check(from_structure((1, None, (2, None, None))), False)

    def test_two_nodes(self):
        self.check(from_structure((1, (2, None, None), (3, None, None))), False)
        self.check(from_structure((1, (2, None, None), (2, None, None))), True)

    def test_crossed_children(self):
        # The same value 3 hangs left on the left branch and right on the right
        # branch: mirrored shapes with equal values, so it is symmetric.
        self.check(from_structure((1, (2, (3, None, None), None),
                                   (2, None, (3, None, None)))), True)
        self.check(from_structure((1, (2, None, (3, None, None)),
                                   (2, (3, None, None), None))), True)
        # Both 3s hang on the same side, so the mirror fails at that pair.
        self.check(from_structure((1, (2, (3, None, None), None),
                                   (2, (3, None, None), None))), False)

    def test_perfect_tree_with_one_deep_mismatch(self):
        self.check(from_structure((1, (2, (4, None, None), (5, None, None)),
                                   (2, (5, None, None), (4, None, None)))), True)
        self.check(from_structure((1, (2, (4, None, None), (5, None, None)),
                                   (2, (5, None, None), (6, None, None)))), False)

    def test_same_values_all_the_way_down_still_needs_the_shape(self):
        # Equal values everywhere: a chain must still be rejected, because
        # symmetry is about the shape as much as the values.
        self.assertFalse(self.solve(chain(4, True, 0)))
        self.assertFalse(self.solve(chain(4, False, 0)))
        # A perfect shape is not enough either: the values at mirrored positions
        # must match, and these are all different.
        self.assertFalse(self.solve(complete_tree(7)))
        # The same perfect shape with equal values is symmetric.
        equal = from_structure((0, (0, (0, None, None), (0, None, None)),
                                (0, (0, None, None), (0, None, None))))
        self.assertTrue(self.solve(equal))
        self.assertTrue(structural_oracle(equal))
        self.assertTrue(positional_oracle(equal))

    def test_every_shape_paired_with_its_mirror_is_symmetric(self):
        for size in range(0, 7):
            for shape in shapes(size):
                half = fill_preorder(shape, range(size))
                root = TreeNode(0, from_structure(half), from_structure(mirror(half)))
                with self.subTest(size=size, values=serialize(root)):
                    self.assertTrue(self.solve(root))
                    self.assertTrue(structural_oracle(root))
                    self.assertTrue(positional_oracle(root))

    def test_exhaustive_small_cases(self):
        for size in range(1, 8):
            for shape in shapes(size):
                for values in (list(range(size)), [1] * size, list(range(size, 0, -1))):
                    root = from_structure(fill_preorder(shape, values))
                    with self.subTest(size=size, values=serialize(root)):
                        self.assertEqual(self.solve(root), structural_oracle(root))
                        self.assertEqual(self.solve(root), positional_oracle(root))

    def test_exhaustive_small_cases_with_few_values(self):
        # Repeated values make accidental matches likely, so the shape decides.
        for size in range(1, 7):
            for shape in shapes(size):
                root = from_structure(fill_preorder(shape, [7] * size))
                with self.subTest(size=size, values=serialize(root)):
                    self.assertEqual(self.solve(root), positional_oracle(root))

    def test_randomised_cases(self):
        rng = random.Random(1010)
        for _ in range(400):
            size = rng.randint(1, 40)
            root = from_structure(random_structure(rng, size))
            with self.subTest(size=size):
                self.assertEqual(self.solve(root), structural_oracle(root))
                self.assertEqual(self.solve(root), positional_oracle(root))

    def test_randomised_symmetric_trees(self):
        rng = random.Random(1011)
        for _ in range(100):
            size = rng.randint(0, 25)
            half = random_structure(rng, size)
            root = TreeNode(rng.randint(-100, 100),
                            from_structure(half), from_structure(mirror(half)))
            with self.subTest(size=size):
                self.assertTrue(self.solve(root))

    def test_constraint_sized(self):
        # 1000 nodes is the constraint maximum, including the deepest shapes
        # (which a recursive check would blow the interpreter stack on).
        size = 1000
        for to_the_left in (True, False):
            with self.subTest(to_the_left=to_the_left):
                deep = chain(size, to_the_left, 0)
                self.assertEqual(node_count(deep), size)
                self.assertFalse(self.solve(deep))
                self.assertFalse(positional_oracle(deep))

        # A complete tree with 1000 nodes is not symmetric either: its last level
        # is filled left to right, so the holes all sit on the right.
        filled = complete_tree(size)
        self.assertEqual(node_count(filled), size)
        self.assertFalse(self.solve(filled))
        self.assertFalse(positional_oracle(filled))

        # 499 nodes mirrored around a root: 999 nodes in total, and symmetric.
        half = complete_tree(499)
        symmetric = TreeNode(0, half, mirror_tree(half))
        self.assertEqual(node_count(symmetric), 2 * 499 + 1)
        self.assertTrue(self.solve(symmetric))
        self.assertTrue(structural_oracle(symmetric))
        self.assertTrue(positional_oracle(symmetric))

        # Change the deepest value on one side: its mirror partner no longer
        # matches, so an otherwise symmetric tree is rejected.
        partner = half
        while partner.left is not None:
            partner = partner.left
        damaged = mirror_tree(half)
        target = damaged
        while target.right is not None:
            target = target.right
        self.assertEqual(target.val, partner.val)
        target.val = partner.val + 1 if partner.val < 100 else partner.val - 1
        broken = TreeNode(0, half, damaged)
        self.assertEqual(node_count(broken), 2 * 499 + 1)
        self.assertFalse(self.solve(broken))
        self.assertFalse(structural_oracle(broken))
        self.assertFalse(positional_oracle(broken))


if __name__ == '__main__':
    unittest.main()
