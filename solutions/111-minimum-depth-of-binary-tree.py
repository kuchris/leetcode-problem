# 111. Minimum Depth of Binary Tree
# https://leetcode.com/problems/minimum-depth-of-binary-tree/
#
# A breadth-first walk returns the depth of the first leaf it meets, and BFS
# visits nodes in nondecreasing depth, so that first leaf is a nearest leaf.
#
# The trap this avoids: the answer is NOT 1 + min(depth(left), depth(right))
# with depth(None) = 0. A node with only one child is not a leaf, so a missing
# child must never be counted as a shallow path of length 0; for example
# [1, 2] has minimum depth 2, not 1. BFS sidesteps that because it stops at real
# leaves only.
#
# Invariant: the queue holds (node, depth) pairs in nondecreasing depth order and
# every node pushed has its recorded depth equal to its distance from the root,
# so the first popped node with no children is a nearest leaf.
#
# Time: O(n)   Space: O(w) for the queue (w = tree width, O(n) worst case)

from collections import deque

class Solution:
    def minDepth(self, root: "TreeNode | None") -> int:
        if root is None:
            return 0

        queue = deque([(root, 1)])
        while queue:
            node, depth = queue.popleft()
            if node.left is None and node.right is None:
                return depth
            if node.left is not None:
                queue.append((node.left, depth + 1))
            if node.right is not None:
                queue.append((node.right, depth + 1))

        return 0  # unreachable: the queue always contains a leaf for a non-empty tree
