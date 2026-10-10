# 114. Flatten Binary Tree to Linked List
# https://leetcode.com/problems/flatten-binary-tree-to-linked-list/
#
# Pre-order flattening in place with O(1) extra space. Walk down the right
# spine; whenever the current node has a left subtree, that subtree must come
# immediately after the node in pre-order, and the old right subtree must follow
# the rightmost node of that left subtree. So:
#
#   - find the predecessor = rightmost node of node.left (following .right from
#     node.left, which does not touch the not-yet-processed right spine),
#   - predecessor.right = node.right (splice the old right subtree after it),
#   - node.right = node.left and node.left = None (move the left subtree up).
#
# Invariant: every node already passed on `node`'s right spine has its left
# pointer cleared and its right subtree replaced by the pre-order continuation,
# so advancing node = node.right walks the pre-order sequence. Each node's left
# subtree is moved up exactly once and every edge is walked at most twice, so
# the total work is linear.
#
# Time: O(n)   Space: O(1) beyond the tree itself

class Solution:
    def flatten(self, root: "TreeNode | None") -> None:
        """
        Do not return anything, modify root in-place instead.
        """
        node = root
        while node is not None:
            if node.left is not None:
                predecessor = node.left
                while predecessor.right is not None:
                    predecessor = predecessor.right
                predecessor.right = node.right
                node.right = node.left
                node.left = None
            node = node.right
