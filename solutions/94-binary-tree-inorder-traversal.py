# 94. Binary Tree Inorder Traversal
# https://leetcode.com/problems/binary-tree-inorder-traversal/
#
# Iterative inorder (the follow-up asks for it): push the whole left spine of
# the current node, then pop, visit, and descend into the popped node's right
# child.
#
# Invariant: the stack holds exactly the ancestors of `node` whose right subtree
# has not been visited yet, in root-to-leaf order, so popping the top yields the
# next value in inorder sequence. Each node is pushed and popped once, and
# `node.right` is only followed after the node itself was emitted.
#
# Time: O(n)   Space: O(h) for the stack (h = tree height, O(n) worst case)

class Solution:
    def inorderTraversal(self, root: "TreeNode | None") -> list[int]:
        result: list[int] = []
        stack: "list[TreeNode]" = []
        node = root
        while stack or node is not None:
            while node is not None:
                stack.append(node)
                node = node.left
            node = stack.pop()
            result.append(node.val)
            node = node.right
        return result
