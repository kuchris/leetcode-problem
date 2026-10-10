# 106. Construct Binary Tree from Inorder and Postorder Traversal
# https://leetcode.com/problems/construct-binary-tree-from-inorder-and-postorder-traversal/
#
# The mirror of problem 105. postorder[-1] is the root, and reading postorder
# backwards visits each node at the moment its right subtree is finished, so the
# same stack walk works with the two sides exchanged: a new value becomes the
# right child while the path has not yet reached the inorder value the sequence
# expects, and otherwise the stack is unwound (matching inorder from the end
# backwards) and the new value is attached as the left child of the last node
# popped.
#
# Invariant: the stack holds the path from the root to the most recently created
# node, and `inorder_index` counts the inorder values already finished, this time
# from the right end. Every postorder value is consumed once and each index is
# pushed and popped once.
#
# Iterative because the constraints allow 3000 nodes in a single chain.
#
# Time: O(n)   Space: O(n)   (n = len(inorder))

class Solution:
    def buildTree(self, inorder: list[int], postorder: list[int]) -> "TreeNode | None":
        if not postorder:
            return None

        root = TreeNode(postorder[-1])
        stack = [root]
        inorder_index = len(inorder) - 1

        for value in reversed(postorder[:-1]):
            node = TreeNode(value)
            if stack[-1].val != inorder[inorder_index]:
                stack[-1].right = node
            else:
                while stack and stack[-1].val == inorder[inorder_index]:
                    parent = stack.pop()
                    inorder_index -= 1
                parent.left = node
            stack.append(node)

        return root
