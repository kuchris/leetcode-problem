# 80. Remove Duplicates from Sorted Array II
# https://leetcode.com/problems/remove-duplicates-from-sorted-array-ii/
#
# One write pointer over a read-only scan of the same array:
#
# Invariant: nums[:write] is always the final prefix -- the input prefix seen so
# far with every run truncated to at most two copies -- and it is sorted, so the
# last two kept values are nums[write - 2] and nums[write - 1].
#
# A scanned value `value` may be kept exactly when the prefix holds fewer than
# two copies of it, i.e. when write < 2 or nums[write - 2] != value. Because the
# array is sorted, all equal values are contiguous, so comparing against the
# value two slots back is enough to count the run: if nums[write - 2] == value
# then nums[write - 1] == value too and the run already has two copies.
# `write <= read` always, so a slot is only overwritten after it has been read.
#
# Time: O(n)   Space: O(1)

class Solution:
    def removeDuplicates(self, nums: list[int]) -> int:
        write = 0
        for value in nums:
            if write < 2 or nums[write - 2] != value:
                nums[write] = value
                write += 1
        return write
