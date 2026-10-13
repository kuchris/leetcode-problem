# 162. Find Peak Element
# https://leetcode.com/problems/find-peak-element/
#
# Binary search on the slope. Think of nums[-1] and nums[n] as -infinity; then a
# peak is a local maximum, and comparing the middle with its right neighbour
# tells which half must contain one:
#
#   - if nums[middle] < nums[middle + 1] the sequence is rising at `middle`, so
#     walking right from `middle` can only stop at a peak (a local maximum of the
#     window, which the -infinity boundary turns into a global peak) -- the
#     window becomes [middle + 1, high];
#   - otherwise it is falling, and a peak lies in [low, middle].
#
# Invariant: a peak always exists inside [low, high], which holds initially for
# the whole array (take any maximal element) and is preserved by both branches
# above. The window shrinks to one index, which is a peak. Adjacent values are
# guaranteed to differ, so the comparison above is never ambiguous.
#
# Time: O(log n)   Space: O(1)

class Solution:
    def findPeakElement(self, nums: list[int]) -> int:
        low, high = 0, len(nums) - 1

        while low < high:
            middle = (low + high) // 2
            if nums[middle] < nums[middle + 1]:
                low = middle + 1
            else:
                high = middle

        return low
