# 153. Find Minimum in Rotated Sorted Array
# https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/
#
# Binary search on the rotation point. In a sorted-then-rotated array with unique
# values, the minimum is the only element smaller than its predecessor, and
# comparing nums[mid] with nums[high] tells which side of the rotation the middle
# sits on:
#
#   - nums[mid] > nums[high]: the drop from the largest to the smallest value
#     happens strictly to the right of mid, so the minimum is in (mid, high];
#   - nums[mid] < nums[high]: nums[mid..high] is one increasing run, so the
#     minimum cannot be past mid and is in [low, mid].
#
# Invariant: the minimum is always inside nums[low..high]. Each step removes at
# least one element, and the loop ends with low == high, so nums[low] is the
# minimum. Rotating n times leaves the array sorted, which the same comparison
# handles because then every nums[mid] < nums[high].
#
# Time: O(log n)   Space: O(1)   (n = len(nums))

class Solution:
    def findMin(self, nums: list[int]) -> int:
        low, high = 0, len(nums) - 1

        while low < high:
            mid = (low + high) // 2
            if nums[mid] > nums[high]:
                low = mid + 1  # the minimum is strictly right of mid
            else:
                high = mid  # nums[mid..high] is increasing; keep mid in range

        return nums[low]
