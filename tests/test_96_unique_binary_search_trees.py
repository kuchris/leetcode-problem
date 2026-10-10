"""Tests for 96. Unique Binary Search Trees.

Oracles:
  - the closed form Catalan(n) = C(2n, n) / (n + 1) from ``math.comb``: it makes
    no use of the recurrence the solution implements, so it is an independent
    authority on the number;
  - the counting brute force: insert every permutation of 1..n into a BST and
    count the distinct serialized shapes. That follows the definition ("how many
    structurally different BSTs") without any combinatorial shortcut, and is
    feasible up to n = 7.
"""

import itertools
import math
import unittest

from _loader import load_solution
from _trees import TreeNode, serialize

Solution = load_solution('96-unique-binary-search-trees.py').Solution


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


def count_by_insertion(n: int) -> int:
    shapes = set()
    for permutation in itertools.permutations(range(1, n + 1)):
        root = None
        for value in permutation:
            root = insert(root, value)
        shapes.add(tuple(serialize(root)))
    return len(shapes)


def catalan_closed_form(n: int) -> int:
    return math.comb(2 * n, n) // (n + 1)


class UniqueBinarySearchTreesTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().numTrees

    def test_official_examples(self):
        self.assertEqual(self.solve(3), 5)
        self.assertEqual(self.solve(1), 1)

    def test_known_small_values(self):
        self.assertEqual(
            [self.solve(n) for n in range(1, 11)],
            [1, 2, 5, 14, 42, 132, 429, 1430, 4862, 16796],
        )

    def test_all_sizes_against_closed_form(self):
        for n in range(1, 20):
            with self.subTest(n=n):
                self.assertEqual(self.solve(n), catalan_closed_form(n))

    def test_exhaustive_small_cases_against_insertion_oracle(self):
        for n in range(1, 8):
            with self.subTest(n=n):
                self.assertEqual(self.solve(n), count_by_insertion(n))

    def test_matches_problem_95_answer_counts(self):
        # The two sibling problems must agree: 95 returns the trees themselves.
        generate = load_solution('95-unique-binary-search-trees-ii.py')
        generate.TreeNode = TreeNode
        for n in range(1, 9):
            with self.subTest(n=n):
                self.assertEqual(len(generate.Solution().generateTrees(n)), self.solve(n))

    def test_growth_is_not_accidentally_linear(self):
        for n in range(2, 19):
            with self.subTest(n=n):
                ratio = self.solve(n) / self.solve(n - 1)
                self.assertGreater(ratio, 1.9)
                self.assertLess(ratio, 4.0)

    def test_constraint_sized(self):
        # n = 19 is the constraint maximum; the answer is the 19th Catalan number.
        self.assertEqual(self.solve(19), 1767263190)
        self.assertEqual(self.solve(19), catalan_closed_form(19))
        self.assertEqual(self.solve(18), catalan_closed_form(18))


if __name__ == '__main__':
    unittest.main()
