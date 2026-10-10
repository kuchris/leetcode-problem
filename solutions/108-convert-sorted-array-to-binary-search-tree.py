# 108. Convert Sorted Array to Binary Search Tree
# https://leetcode.com/problems/convert-sorted-array-to-binary-search-tree/
#
# Take the middle element as the root. Because nums is sorted, everything to its
# left is smaller and everything to its right is larger, so the BST property
# holds for the root and is preserved recursively on both halves. Splitting each
# range in the middle also keeps the subtree sizes within one of each other,
# which is exactly the height-balance requirement.
#
# Invariant: `build(low, high)` returns a height-balanced BST holding exactly
# nums[low:high + 1], and its height is O(log(high - low + 1)) because each step
# halves the range. The empty range is the base case.
#
# Time: O(n)   Space: O(log n) recursion depth   (n = len(nums); the answer tree
# itself is the output)

class Solution:
    def sortedArrayToBST(self, nums: list[int]) -> "TreeNode | None":
        def build(low: int, high: int) -> "TreeNode | None":
            if low > high:
                return None
            middle = (low + high) // 2
            node = TreeNode(nums[middle])
            node.left = build(low, middle - 1)
            node.right = build(middle + 1, high)
            return node

        return build(0, len(nums) - 1)
