# 145. Binary Tree Postorder Traversal
# https://leetcode.com/problems/binary-tree-postorder-traversal/
#
# Iterative version (the follow-up asks for one). Postorder is left, right,
# root; a preorder-style walk that goes root, right, left therefore produces the
# exact reverse of it. The stack pushes the left child before the right one so
# the right subtree is popped (and emitted) first, and the collected values are
# reversed once at the end.
#
# Invariant: each node is pushed and popped exactly once, and it is emitted
# before either of its children; after the reversal every node follows both of
# its subtrees, which is precisely postorder.
#
# Time: O(n)   Space: O(n) for the stack (live depth O(h)) and the output

class Solution:
    def postorderTraversal(self, root: "TreeNode | None") -> list[int]:
        values: list[int] = []
        stack = [root] if root is not None else []
        while stack:
            node = stack.pop()
            values.append(node.val)
            if node.left is not None:
                stack.append(node.left)
            if node.right is not None:
                stack.append(node.right)
        values.reverse()
        return values
