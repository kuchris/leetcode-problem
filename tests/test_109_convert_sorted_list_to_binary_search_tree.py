"""Tests for 109. Convert Sorted List to Binary Search Tree.

LeetCode accepts *any* height-balanced BST over the same values, so comparing
structures would be wrong. The oracle is therefore the definition applied to the
produced tree:

  - its inorder sequence must equal the input list,
  - at every node |height(left) - height(right)| <= 1,
  - it must contain exactly as many nodes as the input list,
  - and it must be built from fresh nodes, leaving the input list untouched.

Height and inorder are recomputed here with an iterative post-order / stack walk,
independently of the solution's recursive midpoint splitting. A second,
independent *construction* (slow/fast pointers on the linked list) confirms that
a balanced tree with this inorder exists, and the solution is additionally
checked to achieve the minimum possible height ceil(log2(n + 1)).
"""

import unittest

from _lists import ListNode, build, to_list
from _loader import load_solution
from _trees import TreeNode

module = load_solution('109-convert-sorted-list-to-binary-search-tree.py')
module.ListNode = ListNode
module.TreeNode = TreeNode
Solution = module.Solution


def inorder_values(root) -> list:
    values = []
    stack = []
    node = root
    while stack or node is not None:
        while node is not None:
            stack.append(node)
            node = node.left
        node = stack.pop()
        values.append(node.val)
        node = node.right
    return values


def heights(root) -> dict:
    """id(node) -> height, computed with an iterative post-order walk."""
    result = {}
    if root is None:
        return result
    stack = [(root, False)]
    while stack:
        node, expanded = stack.pop()
        if not expanded:
            stack.append((node, True))
            if node.right is not None:
                stack.append((node.right, False))
            if node.left is not None:
                stack.append((node.left, False))
            continue
        left = result[id(node.left)] if node.left is not None else 0
        right = result[id(node.right)] if node.right is not None else 0
        result[id(node)] = 1 + max(left, right)
    return result


def tree_height(root) -> int:
    table = heights(root)
    return table[id(root)] if root is not None else 0


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


def assert_balanced(test: unittest.TestCase, root):
    """Every node must have children heights differing by at most one."""
    table = heights(root)
    stack = [root] if root is not None else []
    while stack:
        node = stack.pop()
        left = table[id(node.left)] if node.left is not None else 0
        right = table[id(node.right)] if node.right is not None else 0
        test.assertLessEqual(abs(left - right), 1, f'imbalance at node {node.val}')
        if node.left is not None:
            stack.append(node.left)
        if node.right is not None:
            stack.append(node.right)


def construction_oracle(values) -> "TreeNode | None":
    """Independent build: find the middle with slow/fast pointers each time."""
    head = None
    for value in reversed(list(values)):
        head = ListNode(value, head)

    def convert(node):
        if node is None:
            return None
        # slow/fast pointers to the middle; `before` trails slow.
        before = None
        slow = node
        fast = node
        while fast is not None and fast.next is not None:
            before = slow
            slow = slow.next
            fast = fast.next.next
        left_head = node if before is not None else None
        if before is not None:
            before.next = None
        return TreeNode(slow.val, convert(left_head), convert(slow.next))

    return convert(head)


class ConvertSortedListToBinarySearchTreeTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().sortedListToBST

    def check(self, values):
        head = build(values)
        root = self.solve(head)
        # The list must be untouched (and acyclic).
        self.assertEqual(to_list(head), list(values), 'the input list was modified')
        self.assertEqual(inorder_values(root), list(values))
        self.assertEqual(node_count(root), len(values))
        assert_balanced(self, root)
        return root

    def test_official_examples(self):
        root = self.check([-10, -3, 0, 5, 9])
        self.assertEqual(root.val, 0)
        self.assertIsNone(self.solve(None))

    def test_official_example_is_one_of_the_valid_answers(self):
        # [0,-3,9,-10,null,5] is the answer LeetCode prints; any balanced tree
        # with the same inorder is accepted, including this one.
        expected = TreeNode(0, TreeNode(-3, TreeNode(-10), None), TreeNode(9, TreeNode(5)))
        self.assertEqual(inorder_values(expected), [-10, -3, 0, 5, 9])
        assert_balanced(self, expected)

    def test_small_sizes(self):
        for size in range(0, 20):
            values = list(range(size))
            with self.subTest(size=size):
                root = self.check(values)
                # The midpoint split achieves the minimum possible height.
                self.assertEqual(tree_height(root), (size + 1 - 1).bit_length())

    def test_duplicate_values(self):
        self.check([1, 1])
        self.check([1, 1, 1, 1, 1])
        self.check([-5, -5, 0, 0, 0, 3, 3])
        self.check([0] * 40)

    def test_negative_and_boundary_values(self):
        self.check([-100_000])
        self.check([-100_000, 100_000])
        self.check([-100_000, -100_000, -100_000, 100_000, 100_000])

    def test_exhaustive_small_cases_against_properties(self):
        for size in range(0, 13):
            values = list(range(size))
            with self.subTest(size=size):
                self.check(values)
                oracle_root = construction_oracle(values)
                # The independent construction must satisfy the same properties.
                self.assertEqual(inorder_values(oracle_root), values)
                assert_balanced(self, oracle_root)

    def test_random_cases(self):
        import random

        rng = random.Random(1090)
        for _ in range(200):
            size = rng.randint(0, 200)
            values = sorted(rng.randint(-100_000, 100_000) for _ in range(size))
            with self.subTest(size=size):
                self.check(values)

    def test_constraint_sized(self):
        # 2 * 10^4 nodes is the constraint maximum.
        values = list(range(20_000))
        root = self.check(values)
        self.assertEqual(tree_height(root), (20_000 + 1 - 1).bit_length())

        values = [7] * 20_000
        self.check(values)


if __name__ == '__main__':
    unittest.main()
