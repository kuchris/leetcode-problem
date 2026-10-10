# 105. Construct Binary Tree from Preorder and Inorder Traversal
# https://leetcode.com/problems/construct-binary-tree-from-preorder-and-inorder-traversal/
#
# Iterative construction driven by the inorder array. preorder[0] is the root,
# and every later preorder value is the next node in a depth-first descent, so
# the tree can be built by walking preorder once while keeping the current
# descent path on a stack:
#
#   - If the node on top of the stack is not the next unconsumed inorder value,
#     that node still has an unvisited left subtree, so the new value becomes its
#     left child and joins the path.
#   - Otherwise the path has reached the node the inorder sequence expects next,
#     which means that node's left subtree (and possibly a whole run of finished
#     nodes) is complete: the stack is unwound while its top matches inorder,
#     advancing the pointer each time, and the new value is attached as the right
#     child of the last node popped.
#
# Invariant: the stack always holds the path from the root to the most recently
# created node, and `inorder_index` counts the inorder values already finished.
# Every preorder value is consumed once and each index is pushed and popped once.
#
# Iterative because the constraints allow 3000 nodes in a single chain.
#
# Time: O(n)   Space: O(n)   (n = len(preorder))

class Solution:
    def buildTree(self, preorder: list[int], inorder: list[int]) -> "TreeNode | None":
        if not preorder:
            return None

        root = TreeNode(preorder[0])
        stack = [root]
        inorder_index = 0

        for value in preorder[1:]:
            node = TreeNode(value)
            if stack[-1].val != inorder[inorder_index]:
                stack[-1].left = node
            else:
                while stack and stack[-1].val == inorder[inorder_index]:
                    parent = stack.pop()
                    inorder_index += 1
                parent.right = node
            stack.append(node)

        return root
