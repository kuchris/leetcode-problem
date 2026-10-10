# 154. Find Minimum in Rotated Sorted Array II
# https://leetcode.com/problems/find-minimum-in-rotated-sorted-array-ii/
#
# Same rotation-point binary search as the duplicate-free version, plus the case
# the duplicates create:
#
#   - nums[mid] > nums[high]: the drop is strictly right of mid, minimum in (mid, high];
#   - nums[mid] < nums[high]: nums[mid..high] is increasing, minimum in [low, mid];
#   - nums[mid] == nums[high]: the comparison is uninformative, but nums[high] can
#     simply be discarded -- nums[mid] holds the same value and stays in range, so
#     dropping one copy can never drop the last occurrence of the minimum.
#
# Invariant: the minimum is still inside nums[low..high] after every step. The
# equality branch removes only one element, so an array of equal values costs
# O(n) comparisons; that is unavoidable, because with duplicates the answer can
# only be pinned down by looking at every distinct value.
#
# Time: O(log n) average, O(n) worst case   Space: O(1)   (n = len(nums))

class Solution:
    def findMin(self, nums: list[int]) -> int:
        low, high = 0, len(nums) - 1

        while low < high:
            mid = (low + high) // 2
            if nums[mid] > nums[high]:
                low = mid + 1  # the minimum is strictly right of mid
            elif nums[mid] < nums[high]:
                high = mid  # nums[mid..high] is increasing; keep mid in range
            else:
                high -= 1  # equal values: nums[mid] keeps the value in range

        return nums[low]
