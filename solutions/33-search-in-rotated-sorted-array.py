# 33. Search in Rotated Sorted Array
# https://leetcode.com/problems/search-in-rotated-sorted-array/
#
# A rotated sorted array still has one property that binary search can use: for
# any midpoint, at least one of the two halves is genuinely sorted. Compare
# nums[low] with nums[mid] to tell which side that is, then check whether the
# target lies inside that sorted range. If it does, search there; otherwise the
# target can only be in the other half. The search space halves each step.
#
# Time: O(log n)   Space: O(1)

class Solution:
    def search(self, nums: list[int], target: int) -> int:
        low, high = 0, len(nums) - 1

        while low <= high:
            mid = (low + high) // 2
            if nums[mid] == target:
                return mid

            if nums[low] <= nums[mid]:
                # nums[low..mid] is sorted.
                if nums[low] <= target < nums[mid]:
                    high = mid - 1
                else:
                    low = mid + 1
            else:
                # nums[mid..high] is sorted.
                if nums[mid] < target <= nums[high]:
                    low = mid + 1
                else:
                    high = mid - 1

        return -1
