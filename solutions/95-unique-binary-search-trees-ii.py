# 95. Unique Binary Search Trees II
# https://leetcode.com/problems/unique-binary-search-trees-ii/
#
# Divide and conquer over the value interval [lo, hi]: every value r in the
# interval can be the root, and then the left subtree is any BST built from
# [lo, r-1] and the right subtree any BST from [r+1, hi].
#
# Invariant / correctness: a BST over a set of consecutive values is uniquely
# determined by its root, and the BST ordering puts exactly [lo, r-1] in the
# left subtree and [r+1, hi] in the right one, so enumerating every choice of
# root together with every pair of sub-results enumerates each distinct shape
# exactly once (no duplicates, nothing missing). `hi < lo` is the empty tree,
# represented by the single result None.
#
# The shapes are collected as immutable (value, left, right) tuples and every
# tree is materialised afterwards, so no TreeNode object is ever shared between
# two answers: sharing would alias separate trees together, and mutating one
# result would silently change another.
#
# Time: O(n * C(n)) to materialise C(n) trees of n nodes each   Space: O(n * C(n))
#       for the result, C(n) = Catalan(n) = number of BSTs (C(8) = 1430)

class Solution:
    def generateTrees(self, n: int) -> list["TreeNode | None"]:
        def shapes(lo: int, hi: int) -> list:
            """All BST shapes over [lo, hi] as immutable (value, left, right)."""
            if lo > hi:
                return [None]
            result = []
            for root_value in range(lo, hi + 1):
                for left in shapes(lo, root_value - 1):
                    for right in shapes(root_value + 1, hi):
                        result.append((root_value, left, right))
            return result

        def materialize(shape) -> "TreeNode | None":
            if shape is None:
                return None
            value, left, right = shape
            return TreeNode(value, materialize(left), materialize(right))

        return [materialize(shape) for shape in shapes(1, n)]
