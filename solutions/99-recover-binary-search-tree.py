# 99. Recover Binary Search Tree
# https://leetcode.com/problems/recover-binary-search-tree/
#
# Inorder traversal of a BST is strictly increasing, so swapping the values of
# two nodes can only break that order at the (at most two) places where a key is
# followed by a smaller key:
#
#   - both misplaced keys are adjacent in inorder (one descent p > c): the two
#     swapped nodes are p and c;
#   - they are not adjacent (two descents p1 > c1 and p2 > c2): the first node
#     is p1 and the second is c2.
#
# Invariant of the loop: `previous` is the node emitted just before `node` in
# inorder, `first` is the larger node of the first descent seen, and `second` is
# the smaller node of the most recent descent. Once the traversal ends, swapping
# the values of `first` and `second` restores the sorted inorder sequence, and
# because the tree shape is untouched the tree is a BST again.
#
# Time: O(n)   Space: O(h) for the stack (h = tree height, O(n) worst case)

class Solution:
    def recoverTree(self, root: "TreeNode | None") -> None:
        """
        Do not return anything, modify root in-place instead.
        """
        stack: "list[TreeNode]" = []
        node = root
        previous = None
        first = None
        second = None
        while stack or node is not None:
            while node is not None:
                stack.append(node)
                node = node.left
            node = stack.pop()
            if previous is not None and previous.val > node.val:
                if first is None:
                    first = previous
                second = node
            previous = node
            node = node.right

        if first is not None and second is not None:
            first.val, second.val = second.val, first.val
