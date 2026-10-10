# 144. Binary Tree Preorder Traversal
# https://leetcode.com/problems/binary-tree-preorder-traversal/
#
# Iterative preorder (the follow-up asks for it): pop a node, emit it, then push
# its right child before its left child so the left child is popped first.
#
# Invariant: the stack contains exactly the not-yet-visited nodes whose parents
# were already emitted, ordered so that the top is the next node of the preorder
# sequence; pushing right before left maintains that order, because a stack
# reverses what is pushed. Every node is pushed and popped once.
#
# Time: O(n)   Space: O(h) beyond the output (h = tree height, O(n) worst case)

class Solution:
    def preorderTraversal(self, root: "TreeNode | None") -> list[int]:
        result: list[int] = []
        stack: "list[TreeNode]" = [root] if root is not None else []
        while stack:
            node = stack.pop()
            result.append(node.val)
            if node.right is not None:
                stack.append(node.right)
            if node.left is not None:
                stack.append(node.left)
        return result
