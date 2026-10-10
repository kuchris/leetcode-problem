# 101. Symmetric Tree
# https://leetcode.com/problems/symmetric-tree/
#
# The tree is a mirror of itself when the left subtree is the mirror image of the
# right subtree. That condition is checked pairwise with an explicit stack
# instead of recursion, because the node count reaches 1000 and a degenerate
# tree would nest that deep.
#
# Invariant: every pair on the stack must be a mirror pair, i.e. either both are
# missing, or they carry equal values and their children pair up crossed:
# left.left with right.right and left.right with right.left. Pushing the two
# crossed pairs keeps that requirement, and a pair that fails it proves the tree
# is not symmetric.
#
# Time: O(n)   Space: O(n)   (n = number of nodes; the stack holds at most one
# frontier of pairs)

class Solution:
    def isSymmetric(self, root: "TreeNode | None") -> bool:
        if root is None:
            return True

        stack = [(root.left, root.right)]
        while stack:
            left, right = stack.pop()
            if left is None and right is None:
                continue
            if left is None or right is None or left.val != right.val:
                return False
            stack.append((left.left, right.right))
            stack.append((left.right, right.left))

        return True
