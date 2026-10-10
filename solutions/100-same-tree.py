# 100. Same Tree
# https://leetcode.com/problems/same-tree/
#
# Two trees are the same iff their roots agree on "missing or not" and on the
# value, and their left and right subtrees are pairwise the same. That is a
# simultaneous traversal: keep a stack of node pairs, and for every pair either
# both are None (fine, nothing to explore), or exactly one is None / the values
# differ (False), or both exist (push both child pairs).
#
# Invariant: every pair popped from the stack roots two subtrees that still need
# to be compared, and a False is returned exactly when one of those comparisons
# fails, so reaching an empty stack means every corresponding position matched.
#
# Time: O(n) where n is the number of compared node pairs   Space: O(h)

class Solution:
    def isSameTree(self, p: "TreeNode | None", q: "TreeNode | None") -> bool:
        stack: "list[tuple[TreeNode | None, TreeNode | None]]" = [(p, q)]
        while stack:
            a, b = stack.pop()
            if a is None and b is None:
                continue
            if a is None or b is None or a.val != b.val:
                return False
            stack.append((a.left, b.left))
            stack.append((a.right, b.right))
        return True
