# 34. Find First and Last Position of Element in Sorted Array
# https://leetcode.com/problems/find-first-and-last-position-of-element-in-sorted-array/
#
# Two binary searches instead of one scan. `lower_bound(goal)` returns the first
# index whose value is >= goal, so:
#
#   - lower_bound(target) is the first occurrence, if it exists at all;
#   - lower_bound(target + 1) - 1 is the last occurrence, because the first
#     value greater than target sits immediately after the run of target values.
#
# Using target + 1 rather than an explicit upper-bound variant keeps one helper
# and works for any integer range.
#
# Time: O(log n)   Space: O(1)

class Solution:
    def searchRange(self, nums: list[int], target: int) -> list[int]:
        def lower_bound(goal: int) -> int:
            """First index with nums[index] >= goal (len(nums) if none)."""
            low, high = 0, len(nums)
            while low < high:
                mid = (low + high) // 2
                if nums[mid] < goal:
                    low = mid + 1
                else:
                    high = mid
            return low

        start = lower_bound(target)
        if start == len(nums) or nums[start] != target:
            return [-1, -1]

        return [start, lower_bound(target + 1) - 1]
