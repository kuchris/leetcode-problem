# 124. Binary Tree Maximum Path Sum
# https://leetcode.com/problems/binary-tree-maximum-path-sum/
#
# A path has one highest node (its LCA). At that node it may descend into the
# left child, the right child, both, or neither, so the best path whose top is v
# is v.val + max(0, downward gain of the left child) + max(0, downward gain of
# the right child). The `gain` of v itself is the best sum of a straight descent
# starting at v: v.val + the larger of the two (clamped) child gains.
#
# Invariant: the explicit-stack post-order guarantees a node is expanded only
# after both children were expanded, so `gain[child]` is already final when the
# parent is evaluated. `best` keeps the maximum over every node treated as the
# path's top. The explicit stack avoids the recursion-depth limit on a 3 * 10^4
# node chain.
#
# Time: O(n)   Space: O(n) for the stack and the gain table

class Solution:
    def maxPathSum(self, root: "TreeNode | None") -> int:
        if root is None:
            return 0
        best = -10 ** 18
        gain = {}
        stack = [(root, False)]
        while stack:
            node, expanded = stack.pop()
            if not expanded:
                stack.append((node, True))
                for child in (node.left, node.right):
                    if child is not None:
                        stack.append((child, False))
                continue
            left = gain.get(node.left, 0)
            right = gain.get(node.right, 0)
            left = left if left > 0 else 0
            right = right if right > 0 else 0
            if node.val + left + right > best:
                best = node.val + left + right
            gain[node] = node.val + (left if left > right else right)
        return best
