# 41. First Missing Positive
# https://leetcode.com/problems/first-missing-positive/
#
# With n values, the answer must lie in [1, n + 1]: if all of 1..n are present
# the answer is n + 1, and otherwise some value in that range is absent. That
# bound is what allows the array itself to serve as the hash table.
#
# Place every value v with 1 <= v <= n at index v - 1. The swap loop is safe
# because each swap puts one value into its final slot and never removes a
# correctly placed one, so the total number of swaps is at most n. A second pass
# then reports the first index whose value is not index + 1.
#
# Time: O(n)  (each element is swapped into place at most once)   Space: O(1)

class Solution:
    def firstMissingPositive(self, nums: list[int]) -> int:
        n = len(nums)

        for i in range(n):
            while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
                destination = nums[i] - 1
                nums[i], nums[destination] = nums[destination], nums[i]

        for i in range(n):
            if nums[i] != i + 1:
                return i + 1

        return n + 1
