# 112. Path Sum
# https://leetcode.com/problems/path-sum/
#
# DFS from the root carrying the remaining sum (targetSum minus the values on
# the current path). The answer is True exactly when some popped node is a leaf
# (no children) and its remaining sum is 0.
#
# Invariant: a stack entry (node, remaining) means "the path from the root to
# node has sum targetSum - remaining", which holds for the root entry and is
# preserved when a child is pushed with remaining - child.val. Testing the sum
# only at a leaf implements "root-to-leaf path": a node with one child is not a
# leaf, so a matching prefix does not count. An empty tree has no paths at all,
# hence False even when targetSum == 0.
#
# Time: O(n)   Space: O(h) for the stack (h = tree height, O(n) worst case)

class Solution:
    def hasPathSum(self, root: "TreeNode | None", targetSum: int) -> bool:
        if root is None:
            return False

        stack: "list[tuple[TreeNode, int]]" = [(root, targetSum - root.val)]
        while stack:
            node, remaining = stack.pop()
            if node.left is None and node.right is None:
                if remaining == 0:
                    return True
                continue
            if node.left is not None:
                stack.append((node.left, remaining - node.left.val))
            if node.right is not None:
                stack.append((node.right, remaining - node.right.val))
        return False
