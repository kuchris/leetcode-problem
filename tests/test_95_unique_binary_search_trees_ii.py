"""Tests for 95. Unique Binary Search Trees II.

Oracles:
  - the insertion oracle: insert every permutation of 1..n into a BST and
    deduplicate the serialized shapes. It enumerates the same set from the
    "insert one key at a time" definition, with no divide-and-conquer reasoning,
    so it is an independent authority on which shapes must appear;
  - completeness by counting: the answer must have Catalan(n) entries, each a
    BST holding exactly 1..n, with no duplicates.
"""

import itertools
import math
import unittest

from _trees import TreeNode, load_tree_solution, serialize

Solution = load_tree_solution('95-unique-binary-search-trees-ii.py').Solution


def insert(root, value):
    if root is None:
        return TreeNode(value)
    node = root
    while True:
        if value < node.val:
            if node.left is None:
                node.left = TreeNode(value)
                return root
            node = node.left
        else:
            if node.right is None:
                node.right = TreeNode(value)
                return root
            node = node.right


def insertion_oracle(n: int) -> set:
    """Every distinct BST over 1..n, keyed by its level-order serialization."""
    shapes = set()
    for permutation in itertools.permutations(range(1, n + 1)):
        root = None
        for value in permutation:
            root = insert(root, value)
        shapes.add(tuple(serialize(root)))
    return shapes


def inorder(root) -> list[int]:
    if root is None:
        return []
    return inorder(root.left) + [root.val] + inorder(root.right)


def is_bst(root, low=float('-inf'), high=float('inf')) -> bool:
    if root is None:
        return True
    if not low < root.val < high:
        return False
    return is_bst(root.left, low, root.val) and is_bst(root.right, root.val, high)


def catalan(n: int) -> int:
    return math.comb(2 * n, n) // (n + 1)


def all_nodes(root, out=None) -> list:
    if out is None:
        out = []
    if root is None:
        return out
    out.append(root)
    all_nodes(root.left, out)
    all_nodes(root.right, out)
    return out


class UniqueBinarySearchTreesIITests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().generateTrees

    def keys(self, n):
        return sorted(tuple(serialize(root)) for root in self.solve(n))

    def test_official_examples(self):
        expected = {
            (1, None, 2, None, 3),
            (1, None, 3, 2),
            (2, 1, 3),
            (3, 1, None, None, 2),
            (3, 2, None, 1),
        }
        self.assertEqual({tuple(key) for key in self.keys(3)}, expected)
        self.assertEqual(self.keys(1), [(1,)])

    def test_every_answer_is_a_bst_with_values_one_to_n(self):
        for n in range(1, 9):
            for root in self.solve(n):
                with self.subTest(n=n, tree=serialize(root)):
                    self.assertTrue(is_bst(root))
                    self.assertEqual(inorder(root), list(range(1, n + 1)))

    def test_counts_match_catalan_numbers(self):
        for n in range(1, 9):
            with self.subTest(n=n):
                self.assertEqual(len(self.solve(n)), catalan(n))

    def test_no_duplicate_shapes(self):
        for n in range(1, 9):
            with self.subTest(n=n):
                keys = [tuple(serialize(root)) for root in self.solve(n)]
                self.assertEqual(len(keys), len(set(keys)))

    def test_exhaustive_small_cases_against_insertion_oracle(self):
        for n in range(1, 8):
            with self.subTest(n=n):
                self.assertEqual(
                    {tuple(key) for key in self.keys(n)}, insertion_oracle(n)
                )

    def test_answers_do_not_share_nodes(self):
        # Sharing a node between two answers would alias separate trees; the
        # solution rebuilds each sub-result on purpose.
        for n in range(1, 7):
            roots = self.solve(n)
            seen = set()
            for root in roots:
                for node in all_nodes(root):
                    self.assertNotIn(id(node), seen, f'node shared for n={n}')
                    seen.add(id(node))

    def test_constraint_sized(self):
        # n = 8 is the constraint maximum.
        n = 8
        self.assertEqual(len(self.solve(n)), catalan(n))
        for root in self.solve(n):
            self.assertTrue(is_bst(root))
            self.assertEqual(inorder(root), list(range(1, n + 1)))
        # n = 7 is still small enough for the permutation oracle.
        self.assertEqual(
            {tuple(key) for key in self.keys(7)}, insertion_oracle(7)
        )


if __name__ == '__main__':
    unittest.main()
