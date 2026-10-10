# 110. Balanced Binary Tree
# https://leetcode.com/problems/balanced-binary-tree/
#
# Height-balanced means: at every node |height(left) - height(right)| <= 1, and
# both subtrees are balanced as well. A single bottom-up pass is enough, because
# height(node) = 1 + max(height(left), height(right)): once both child heights
# are known the node can be checked and its own height stored.
#
# The traversal is iterative -- a stack of (node, children_done) pairs with the
# finished heights kept in a dict keyed by id(node) -- so a 5000-node chain
# cannot overflow the Python stack. id() is a safe key here because the tree
# keeps every node alive for the whole call, so no two live nodes share one.
#
# Time: O(n)   Space: O(n) for the height table and the stack (O(h) if heights
#       were kept on the nodes)

class Solution:
    def isBalanced(self, root: "TreeNode | None") -> bool:
        if root is None:
            return True

        heights: "dict[int, int]" = {}
        stack: "list[tuple[TreeNode, bool]]" = [(root, False)]
        while stack:
            node, children_done = stack.pop()
            if not children_done:
                stack.append((node, True))
                if node.right is not None:
                    stack.append((node.right, False))
                if node.left is not None:
                    stack.append((node.left, False))
                continue

            left_height = heights[id(node.left)] if node.left is not None else 0
            right_height = heights[id(node.right)] if node.right is not None else 0
            if abs(left_height - right_height) > 1:
                return False
            heights[id(node)] = 1 + (left_height if left_height > right_height
                                     else right_height)

        return True
