# 107. Binary Tree Level Order Traversal II
# https://leetcode.com/problems/binary-tree-level-order-traversal-ii/
#
# Identical level-by-level breadth-first search to 102 (level 102 emits levels
# top-down), with the finished list of levels reversed at the end so the deepest
# level comes first while each level itself stays left to right.
#
# Invariant: `level` holds exactly the nodes of one depth in left-to-right order,
# so `levels` collects the top-down traversal; reversing a list does not disturb
# the order inside its elements.
#
# Iterative because the constraints allow 2000 nodes in a single chain.
#
# Time: O(n)   Space: O(n)   (n = number of nodes)

class Solution:
    def levelOrderBottom(self, root: "TreeNode | None") -> list[list[int]]:
        levels: list[list[int]] = []
        level = [root] if root is not None else []

        while level:
            levels.append([node.val for node in level])
            following: list = []
            for node in level:
                if node.left is not None:
                    following.append(node.left)
                if node.right is not None:
                    following.append(node.right)
            level = following

        levels.reverse()
        return levels
