# 26. Remove Duplicates from Sorted Array
# https://leetcode.com/problems/remove-duplicates-from-sorted-array/
#
# Because the array is sorted, equal values are adjacent, so a single pass can
# compact the uniques into the front. `write` marks where the next unique value
# belongs and `read` scans forward; a value is new exactly when it differs from
# the last one written.
#
# Time: O(n)   Space: O(1)

class Solution:
    def removeDuplicates(self, nums: list[int]) -> int:
        if not nums:
            return 0

        write = 1
        for read in range(1, len(nums)):
            if nums[read] != nums[write - 1]:
                nums[write] = nums[read]
                write += 1

        return write
