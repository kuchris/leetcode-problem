"""Tests for 105. Construct Binary Tree from Preorder and Inorder Traversal.

Two independent checks:

  - brute force: enumerate every binary tree shape with n nodes, fill it with the
    inorder values in inorder order (so that inorder matches by construction),
    and keep the shape whose preorder equals the input. That generate-and-test
    search finds the unique answer without any reconstruction algorithm of its
    own, and the solution's structure must equal it.
  - contract: for sizes where enumeration is hopeless (up to 3000 nodes) verify
    the defining properties of the produced tree directly -- an iterative
    preorder walk must reproduce the preorder input, an iterative inorder walk
    must reproduce the inorder input, the node count must match, and no node
    object may be shared (which also rules out a cycle).

All traversal helpers here are iterative so the 3000-node chains stay checkable,
and the reference trees are built from shapes rather than from the solution.
"""

import random
import unittest

from _trees import TreeNode, from_structure, load_tree_solution, serialize, to_structure

module = load_tree_solution('105-construct-binary-tree-from-preorder-and-inorder-traversal.py')
Solution = module.Solution


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


def fill_inorder(shape, values):
    """Assign values to a shape in inorder sequence."""
    iterator = iter(values)

    def walk(node):
        if node is None:
            return None
        left = walk(node[0])
        value = next(iterator)
        right = walk(node[1])
        return (value, left, right)

    return walk(shape)


def fill_preorder(shape, values):
    iterator = iter(values)

    def walk(node):
        if node is None:
            return None
        value = next(iterator)
        return (value, walk(node[0]), walk(node[1]))

    return walk(shape)


def preorder_of(structure) -> list:
    if structure is None:
        return []
    value, left, right = structure
    return [value] + preorder_of(left) + preorder_of(right)


def brute_force_build(preorder, inorder):
    """The unique tree with that preorder and inorder, found by enumeration."""
    for shape in shapes(len(inorder)):
        filled = fill_inorder(shape, inorder)
        if preorder_of(filled) == list(preorder):
            return filled
    return None


def preorder_values(root) -> list:
    out = []
    stack = [root] if root is not None else []
    while stack:
        node = stack.pop()
        out.append(node.val)
        if node.right is not None:
            stack.append(node.right)
        if node.left is not None:
            stack.append(node.left)
    return out


def inorder_values(root) -> list:
    out = []
    stack = []
    node = root
    while stack or node is not None:
        while node is not None:
            stack.append(node)
            node = node.left
        node = stack.pop()
        out.append(node.val)
        node = node.right
    return out


def collect_nodes(root) -> list:
    found = []
    stack = [root] if root is not None else []
    while stack:
        node = stack.pop()
        found.append(node)
        if node.left is not None:
            stack.append(node.left)
        if node.right is not None:
            stack.append(node.right)
    return found


def random_shape(rng, size: int):
    if size == 0:
        return None
    left_size = rng.randint(0, size - 1)
    return (random_shape(rng, left_size), random_shape(rng, size - 1 - left_size))


def chain(size: int, to_the_left: bool, values) -> TreeNode:
    """A chain of `size` nodes built iteratively, values consumed in order."""
    root = None
    for value in values:
        root = TreeNode(value, root, None) if to_the_left else TreeNode(value, None, root)
    return root


def build_balanced(values: list) -> TreeNode:
    """A balanced reference tree over the whole list. Depth is O(log n)."""
    def build(low: int, high: int) -> "TreeNode | None":
        if low > high:
            return None
        middle = (low + high) // 2
        node = TreeNode(values[middle])
        node.left = build(low, middle - 1)
        node.right = build(middle + 1, high)
        return node

    return build(0, len(values) - 1)


class ConstructFromPreorderAndInorderTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().buildTree

    def test_official_examples(self):
        root = self.solve([3, 9, 20, 15, 7], [9, 3, 15, 20, 7])
        self.assertEqual(serialize(root), [3, 9, 20, None, None, 15, 7])
        self.assertEqual(to_structure(root), (3, (9, None, None), (20, (15, None, None), (7, None, None))))
        self.assertEqual(serialize(self.solve([-1], [-1])), [-1])

    def test_single_node(self):
        self.assertEqual(serialize(self.solve([5], [5])), [5])
        self.assertEqual(serialize(self.solve([-3000], [-3000])), [-3000])

    def test_chains(self):
        # A right chain: preorder and inorder are both ascending.
        self.assertEqual(serialize(self.solve([1, 2, 3], [1, 2, 3])), [1, None, 2, None, 3])
        # A left chain: preorder is descending, inorder ascending.
        self.assertEqual(serialize(self.solve([3, 2, 1], [1, 2, 3])), [3, 2, None, 1])

    def test_two_and_three_nodes(self):
        self.assertEqual(serialize(self.solve([1, 2], [2, 1])), [1, 2])
        self.assertEqual(serialize(self.solve([1, 2], [1, 2])), [1, None, 2])
        self.assertEqual(serialize(self.solve([2, 1, 3], [1, 2, 3])),
                         [2, 1, 3])

    def test_boundary_values(self):
        preorder = [0, -3000, 3000]
        inorder = [-3000, 0, 3000]
        root = self.solve(preorder, inorder)
        self.assertEqual(inorder_values(root), inorder)
        self.assertEqual(preorder_values(root), preorder)

    def test_exhaustive_shapes(self):
        for size in range(1, 8):
            for shape in shapes(size):
                reference = from_structure(fill_inorder(shape, range(size)))
                preorder = preorder_values(reference)
                inorder = inorder_values(reference)
                with self.subTest(size=size, preorder=preorder, inorder=inorder):
                    result = self.solve(preorder, inorder)
                    self.assertEqual(to_structure(result), to_structure(reference))
                    self.assertEqual(to_structure(result), brute_force_build(preorder, inorder))

    def test_exhaustive_shapes_with_negative_values(self):
        for size in range(1, 7):
            for shape in shapes(size):
                values = [(-3 * index) for index in range(size)]
                reference = from_structure(fill_inorder(shape, values))
                preorder = preorder_values(reference)
                inorder = inorder_values(reference)
                with self.subTest(size=size, inorder=inorder):
                    result = self.solve(preorder, inorder)
                    self.assertEqual(to_structure(result), brute_force_build(preorder, inorder))

    def test_randomised_cases(self):
        rng = random.Random(1050)
        for _ in range(150):
            size = rng.randint(1, 60)
            values = rng.sample(range(-3000, 3001), size)
            reference = from_structure(fill_preorder(random_shape(rng, size), values))
            preorder = preorder_values(reference)
            inorder = inorder_values(reference)
            with self.subTest(size=size):
                result = self.solve(preorder, inorder)
                self.assertEqual(to_structure(result), to_structure(reference))
                if size <= 7:
                    self.assertEqual(to_structure(result), brute_force_build(preorder, inorder))

    def test_result_contract_on_random_trees(self):
        rng = random.Random(1051)
        for _ in range(100):
            size = rng.randint(1, 200)
            values = rng.sample(range(-3000, 3001), size)
            reference = from_structure(fill_preorder(random_shape(rng, size), values))
            preorder = preorder_values(reference)
            inorder = inorder_values(reference)
            with self.subTest(size=size):
                result = self.solve(preorder, inorder)
                self.assertEqual(preorder_values(result), preorder)
                self.assertEqual(inorder_values(result), inorder)
                nodes = collect_nodes(result)
                self.assertEqual(len(nodes), size)
                self.assertEqual(len({id(node) for node in nodes}), size)

    def test_constraint_sized(self):
        # 3000 nodes is the constraint maximum, including the deepest shapes.
        size = 3000
        values = list(range(1, size + 1))

        for to_the_left in (True, False):
            chain_root = chain(size, to_the_left, values)
            preorder = preorder_values(chain_root)
            inorder = inorder_values(chain_root)
            with self.subTest(to_the_left=to_the_left, depth=size):
                result = self.solve(preorder, inorder)
                self.assertEqual(preorder_values(result), preorder)
                self.assertEqual(inorder_values(result), inorder)
                nodes = collect_nodes(result)
                self.assertEqual(len(nodes), size)
                self.assertEqual(len({id(node) for node in nodes}), size)

        # A balanced 3000-node reference tree, rebuilt exactly.
        reference = build_balanced(values)
        preorder = preorder_values(reference)
        inorder = inorder_values(reference)
        result = self.solve(preorder, inorder)
        self.assertEqual(inorder_values(result), inorder)
        self.assertEqual(preorder_values(result), preorder)
        self.assertEqual(len(collect_nodes(result)), size)


if __name__ == '__main__':
    unittest.main()
