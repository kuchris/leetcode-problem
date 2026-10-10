# 102. Binary Tree Level Order Traversal
# https://leetcode.com/problems/binary-tree-level-order-traversal/
#
# Breadth-first search carrying one whole level at a time: `level` is the list of
# nodes at the current depth in left-to-right order, and the next level is built
# by appending each node's left child then its right child.
#
# Invariant: at the start of every iteration `level` holds exactly the nodes of
# one depth, ordered left to right (their parents were processed left to right,
# and each parent contributes left before right). A level is emitted before the
# next one is built, so the output is grouped by depth.
#
# Iterative rather than recursive because the constraints allow 2000 nodes in a
# single chain.
#
# Time: O(n)   Space: O(n)   (n = number of nodes; the widest level dominates)

class Solution:
    def levelOrder(self, root: "TreeNode | None") -> list[list[int]]:
        result: list[list[int]] = []
        level = [root] if root is not None else []

        while level:
            result.append([node.val for node in level])
            following: list = []
            for node in level:
                if node.left is not None:
                    following.append(node.left)
                if node.right is not None:
                    following.append(node.right)
            level = following

        return result
