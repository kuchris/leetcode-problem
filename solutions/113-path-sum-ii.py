# 113. Path Sum II
# https://leetcode.com/problems/path-sum-ii/
#
# Same root-to-leaf DFS as problem 112, but every matching path is collected
# instead of stopping at the first one. Each stack entry carries its own path
# list, so sibling branches never share or mutate one another's path.
#
# Invariant: a stack entry (node, remaining, path) means `path` is exactly the
# root-to-node value sequence and targetSum - remaining is its sum. A path is
# recorded only at a leaf (no children) with remaining == 0, which implements
# "root-to-leaf"; an empty tree yields no paths.
#
# Time: O(n * h) worst case   Space: O(n * h) worst case, O(h) for a chain
#       (h = tree height; each of the n nodes may carry a copy of a path of up
#       to h values, both for the time spent copying and for the stack)

class Solution:
    def pathSum(self, root: "TreeNode | None", targetSum: int) -> list[list[int]]:
        if root is None:
            return []

        results: list[list[int]] = []
        stack: "list[tuple[TreeNode, int, list[int]]]" = [
            (root, targetSum - root.val, [root.val])
        ]
        while stack:
            node, remaining, path = stack.pop()
            if node.left is None and node.right is None:
                if remaining == 0:
                    results.append(path)
                continue
            if node.left is not None:
                stack.append((node.left, remaining - node.left.val, path + [node.left.val]))
            if node.right is not None:
                stack.append((node.right, remaining - node.right.val,
                              path + [node.right.val]))
        return results
