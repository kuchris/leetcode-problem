# 27. Remove Element
# https://leetcode.com/problems/remove-element/
#
# Compact in place: `write` is the next slot for a value that is not `val`, and
# `read` scans every element once. Elements equal to `val` are simply skipped,
# so everything before `write` at the end is exactly the surviving set.
#
# The order of the survivors is preserved, which the judge does not require but
# which costs nothing here.
#
# Time: O(n)   Space: O(1)

class Solution:
    def removeElement(self, nums: list[int], val: int) -> int:
        write = 0
        for read in range(len(nums)):
            if nums[read] != val:
                nums[write] = nums[read]
                write += 1
        return write
