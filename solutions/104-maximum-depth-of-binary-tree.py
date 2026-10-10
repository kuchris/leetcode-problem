# 104. Maximum Depth of Binary Tree
# https://leetcode.com/problems/maximum-depth-of-binary-tree/
#
# The depth is the number of levels, so counting them while walking the tree
# breadth-first gives the answer directly: each round consumes one level and
# builds the next.
#
# Invariant: at the start of each round `level` is exactly the set of nodes at
# depth `depth + 1`, so incrementing `depth` once per round counts levels, and
# the loop exits after the deepest level has been consumed. An empty tree never
# enters the loop and returns 0.
#
# Iterative rather than recursive: the constraints allow 10^4 nodes in a single
# chain, which would overflow Python's default recursion limit.
#
# Time: O(n)   Space: O(n)   (n = number of nodes; the widest level dominates)

class Solution:
    def maxDepth(self, root: "TreeNode | None") -> int:
        depth = 0
        level = [root] if root is not None else []

        while level:
            depth += 1
            following: list = []
            for node in level:
                if node.left is not None:
                    following.append(node.left)
                if node.right is not None:
                    following.append(node.right)
            level = following

        return depth
