# 31. Next Permutation
# https://leetcode.com/problems/next-permutation/
#
# The next permutation is the smallest arrangement that is lexicographically
# larger, so it should change as little as possible from the right:
#
#   1. Find the rightmost index i with nums[i] < nums[i + 1]. Everything to the
#      right of i is non-increasing, hence already the largest arrangement of
#      that suffix, so i is the last position that can be increased.
#   2. Swap nums[i] with the rightmost value greater than it. That value is the
#      smallest possible increase, and the suffix stays non-increasing.
#   3. Reverse the suffix to turn it into its smallest arrangement.
#
# If no such i exists the whole array is non-increasing, so the answer is the
# ascending order produced by reversing the entire array (i = -1).
#
# Time: O(n)   Space: O(1)

class Solution:
    def nextPermutation(self, nums: list[int]) -> None:
        """Do not return anything, modify nums in-place instead."""
        n = len(nums)

        i = n - 2
        while i >= 0 and nums[i] >= nums[i + 1]:
            i -= 1

        if i >= 0:
            j = n - 1
            while nums[j] <= nums[i]:
                j -= 1
            nums[i], nums[j] = nums[j], nums[i]

        # Reverse nums[i + 1:]; with i == -1 this sorts the whole array.
        left, right = i + 1, n - 1
        while left < right:
            nums[left], nums[right] = nums[right], nums[left]
            left += 1
            right -= 1
