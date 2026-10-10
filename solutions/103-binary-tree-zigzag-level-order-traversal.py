# 103. Binary Tree Zigzag Level Order Traversal
# https://leetcode.com/problems/binary-tree-zigzag-level-order-traversal/
#
# Same level-by-level breadth-first search as 102, with the direction flipped
# after every level: level 0 is emitted left to right, level 1 right to left, and
# so on.
#
# Invariant: `level` always holds the nodes of one depth in left-to-right order
# (both children are appended left before right), and `left_to_right` is true
# exactly when the current depth is even. Reversing the collected values for the
# odd depths therefore produces the zigzag order without changing the traversal
# itself.
#
# Iterative because the constraints allow 2000 nodes in a single chain.
#
# Time: O(n)   Space: O(n)   (n = number of nodes)

class Solution:
    def zigzagLevelOrder(self, root: "TreeNode | None") -> list[list[int]]:
        result: list[list[int]] = []
        level = [root] if root is not None else []
        left_to_right = True

        while level:
            values = [node.val for node in level]
            result.append(values if left_to_right else values[::-1])

            following: list = []
            for node in level:
                if node.left is not None:
                    following.append(node.left)
                if node.right is not None:
                    following.append(node.right)
            level = following
            left_to_right = not left_to_right

        return result
