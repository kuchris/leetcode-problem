"""Tests for 108. Convert Sorted Array to Binary Search Tree.

The problem accepts any height-balanced BST, so a single expected tree would be
the wrong oracle. Two checks instead:

  - membership brute force: enumerate every binary tree shape with n nodes, fill
    it with nums in inorder order (which makes it a BST by construction because
    nums is strictly increasing), keep the height-balanced ones, and require the
    solution's structure to be among them. For n <= 7 that set is small enough to
    enumerate exhaustively.
  - the spec itself, for every size: an iterative inorder walk must return nums
    exactly (strictly increasing values make that equivalent to the BST
    property), and every node's two subtree heights must differ by at most one
    (iterative post-order, so the constraint-sized 10^4 case is checkable).

`test_median_split_has_the_minimum_height` is deliberately implementation
specific: it pins the extra guarantee that the middle-element split is optimal,
not merely balanced.
"""

import random
import unittest

from _trees import TreeNode, load_tree_solution, serialize, to_structure

module = load_tree_solution('108-convert-sorted-array-to-binary-search-tree.py')
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


def fill_inorder(shape, values):
    iterator = iter(values)

    def walk(node):
        if node is None:
            return None
        left = walk(node[0])
        value = next(iterator)
        right = walk(node[1])
        return (value, left, right)

    return walk(shape)


def height_of(structure) -> int:
    if structure is None:
        return 0
    _, left, right = structure
    return 1 + max(height_of(left), height_of(right))


def balanced_oracle_structures(nums) -> set:
    """Every height-balanced BST structure over nums, by enumeration."""
    valid = set()
    for shape in shapes(len(nums)):
        filled = fill_inorder(shape, nums)
        if is_balanced_structure(filled):
            valid.add(filled)
    return valid


def is_balanced_structure(structure) -> bool:
    if structure is None:
        return True
    _, left, right = structure
    return (abs(height_of(left) - height_of(right)) <= 1
            and is_balanced_structure(left)
            and is_balanced_structure(right))


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


def subtree_heights(root) -> dict:
    """{id(node): height} computed bottom-up with an explicit post-order stack."""
    heights = {}
    stack = [(root, False)] if root is not None else []
    while stack:
        node, processed = stack.pop()
        if not processed:
            stack.append((node, True))
            if node.left is not None:
                stack.append((node.left, False))
            if node.right is not None:
                stack.append((node.right, False))
            continue
        left_height = heights.get(id(node.left), 0)
        right_height = heights.get(id(node.right), 0)
        heights[id(node)] = 1 + max(left_height, right_height)
    return heights


def unbalanced_node(root):
    """The first node whose subtree heights differ by more than one, or None."""
    if root is None:
        return None
    heights = subtree_heights(root)
    stack = [root]
    while stack:
        node = stack.pop()
        left_height = heights.get(id(node.left), 0)
        right_height = heights.get(id(node.right), 0)
        if abs(left_height - right_height) > 1:
            return node
        if node.left is not None:
            stack.append(node.left)
        if node.right is not None:
            stack.append(node.right)
    return None


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


class ConvertSortedArrayToBinarySearchTreeTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().sortedArrayToBST

    def assert_valid(self, root, nums):
        self.assertEqual(inorder_values(root), list(nums))
        self.assertIsNone(unbalanced_node(root))
        nodes = collect_nodes(root)
        self.assertEqual(len(nodes), len(nums))
        self.assertEqual(len({id(node) for node in nodes}), len(nums))

    def test_official_examples(self):
        nums = [-10, -3, 0, 5, 9]
        root = self.solve(nums)
        self.assert_valid(root, nums)
        # Both serializations named in the statement are accepted; the
        # middle-element split produces the second one.
        self.assertIn(serialize(root), ([0, -3, 9, -10, None, 5],
                                        [0, -10, 5, None, -3, None, 9]))
        self.assertEqual(serialize(self.solve([1, 3])), [1, None, 3])

    def test_single_element(self):
        for value in (-10 ** 4, 0, 10 ** 4):
            with self.subTest(value=value):
                root = self.solve([value])
                self.assertEqual(serialize(root), [value])

    def test_two_elements(self):
        root = self.solve([1, 3])
        self.assert_valid(root, [1, 3])
        self.assertEqual(serialize(root), [1, None, 3])
        root = self.solve([-10 ** 4, 10 ** 4])
        self.assert_valid(root, [-10 ** 4, 10 ** 4])

    def test_boundary_values(self):
        nums = [-10 ** 4, -9999, 0, 9999, 10 ** 4]
        self.assert_valid(self.solve(nums), nums)

    def test_membership_in_the_brute_force_set(self):
        value_sets = [list(range(1, size + 1)) for size in range(1, 8)]
        value_sets += [[-3 * index for index in range(size)] for size in range(1, 8)]
        value_sets += [[index * 7 - 20 for index in range(size)] for size in range(1, 8)]
        for nums in value_sets:
            with self.subTest(nums=nums):
                root = self.solve(nums)
                self.assert_valid(root, nums)
                self.assertIn(to_structure(root), balanced_oracle_structures(nums))

    def test_randomised_cases(self):
        rng = random.Random(1080)
        for _ in range(100):
            size = rng.randint(1, 300)
            nums = sorted(rng.sample(range(-10 ** 4, 10 ** 4 + 1), size))
            with self.subTest(size=size):
                self.assert_valid(self.solve(nums), nums)

    def test_randomised_small_cases_are_in_the_oracle_set(self):
        rng = random.Random(1081)
        for _ in range(40):
            size = rng.randint(1, 7)
            nums = sorted(rng.sample(range(-50, 51), size))
            with self.subTest(nums=nums):
                root = self.solve(nums)
                self.assert_valid(root, nums)
                self.assertIn(to_structure(root), balanced_oracle_structures(nums))

    def test_median_split_has_the_minimum_height(self):
        # Extra guarantee of this implementation: the middle-element split is
        # optimal, not merely height balanced. The minimum possible height for n
        # nodes is ceil(log2(n + 1)), which is n.bit_length().
        for size in range(1, 101):
            nums = list(range(size))
            with self.subTest(size=size):
                root = self.solve(nums)
                self.assertEqual(subtree_heights(root)[id(root)], size.bit_length())

    def test_constraint_sized(self):
        # 10^4 elements is the constraint maximum.
        nums = list(range(-5000, 5000))
        self.assertEqual(len(nums), 10 ** 4)
        root = self.solve(nums)
        self.assert_valid(root, nums)

        rng = random.Random(1082)
        nums = sorted(rng.sample(range(-10 ** 4, 10 ** 4 + 1), 10 ** 4))
        root = self.solve(nums)
        self.assert_valid(root, nums)
        self.assertLessEqual(subtree_heights(root)[id(root)], 15)

        # A value set with no zero and no repeats, still exactly 10^4 elements.
        nums = list(range(-5000, 0)) + list(range(1, 5001))
        self.assertEqual(len(nums), 10 ** 4)
        root = self.solve(nums)
        self.assert_valid(root, nums)


if __name__ == '__main__':
    unittest.main()
