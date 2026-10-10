# 109. Convert Sorted List to Binary Search Tree
# https://leetcode.com/problems/convert-sorted-list-to-binary-search-tree/
#
# A sorted singly linked list is exactly the inorder sequence of the wanted BST.
# The list cannot be indexed in O(1), so the values are copied into an array and
# the tree is built by recursive midpoint splitting of the index range [lo, hi].
#
# Invariant: build(lo, hi) returns a height-balanced BST whose inorder is
# values[lo..hi]. Taking mid = (lo + hi) // 2 as the root leaves
# floor((s-1)/2) values on the left and ceil((s-1)/2) on the right (s = hi-lo+1),
# so the two subtree sizes differ by at most one; by induction both subtrees are
# height-balanced and their heights differ by at most one, which makes the whole
# tree height-balanced. Sorted order is preserved because the left subtree takes
# the smaller indices and the right subtree the larger ones.
#
# Time: O(n)   Space: O(n) for the copied values + O(log n) recursion depth

class Solution:
    def sortedListToBST(self, head: "ListNode | None") -> "TreeNode | None":
        values = []
        node = head
        while node is not None:
            values.append(node.val)
            node = node.next

        def build(lo: int, hi: int) -> "TreeNode | None":
            if lo > hi:
                return None
            mid = (lo + hi) // 2
            return TreeNode(values[mid], build(lo, mid - 1), build(mid + 1, hi))

        return build(0, len(values) - 1)
