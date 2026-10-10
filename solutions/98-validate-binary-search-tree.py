# 98. Validate Binary Search Tree
# https://leetcode.com/problems/validate-binary-search-tree/
#
# A tree is a BST iff its inorder traversal is strictly increasing: inorder
# visits the left subtree, then the node, then the right subtree, and the BST
# condition says exactly that the left subtree's keys are smaller and the right
# subtree's keys are larger, which by induction is the same statement as "each
# key is greater than the previous one emitted".
#
# Implemented iteratively: push the left spine of the current node, pop (that
# pop is the next inorder key), compare with the previous key, then descend into
# the popped node's right child. Checking `<=` also rejects duplicates, which a
# BST forbids.
#
# Time: O(n)   Space: O(h) for the stack (h = tree height, O(n) worst case)

class Solution:
    def isValidBST(self, root: "TreeNode | None") -> bool:
        stack: "list[TreeNode]" = []
        node = root
        previous = None
        while stack or node is not None:
            while node is not None:
                stack.append(node)
                node = node.left
            node = stack.pop()
            if previous is not None and node.val <= previous:
                return False
            previous = node.val
            node = node.right
        return True
