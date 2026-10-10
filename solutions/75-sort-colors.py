# 75. Sort Colors
# https://leetcode.com/problems/sort-colors/
#
# Dutch national flag, one pass with three pointers:
#
#   - everything before `low` is 0, everything after `high` is 2;
#   - `mid` scans the unclassified region between them;
#   - a 0 swaps back to `low` and both pointers advance, since the value pulled
#     into `mid` came from the already-classified 0/1 region;
#   - a 1 just advances `mid`;
#   - a 2 swaps to `high`, and `mid` does not advance because the value pulled
#     in from the right has not been examined yet.
#
# Each element is examined once and swapped at most once.
#
# Time: O(n)   Space: O(1)

class Solution:
    def sortColors(self, nums: list[int]) -> None:
        """Do not return anything, modify nums in-place instead."""
        low, mid, high = 0, 0, len(nums) - 1

        while mid <= high:
            if nums[mid] == 0:
                nums[low], nums[mid] = nums[mid], nums[low]
                low += 1
                mid += 1
            elif nums[mid] == 1:
                mid += 1
            else:
                nums[mid], nums[high] = nums[high], nums[mid]
                high -= 1
