# 90. Subsets II
# https://leetcode.com/problems/subsets-ii/
#
# Sort first, then backtrack with the "one child per distinct value" rule.
#
# Invariant: the recursion visits every distinct subset exactly once. At a call
# with `start`, the path holds a chosen prefix and the loop picks the next
# element from nums[start:]; equal values are contiguous after sorting, so
# skipping nums[index] when it equals nums[index - 1] (and index > start) skips
# exactly the duplicates of a choice already made at this depth. Two different
# index sets that produce the same multiset therefore collapse into one branch:
# the one that always takes the earliest copy of each value.
#
# Every subset is emitted on entry, before recursing, so [] is included.
#
# Time: O(2^n * n)   Space: O(n) recursion depth (output not counted)

class Solution:
    def subsetsWithDup(self, nums: list[int]) -> list[list[int]]:
        nums.sort()
        result: list[list[int]] = []
        path: list[int] = []

        def backtrack(start: int) -> None:
            result.append(path.copy())
            for index in range(start, len(nums)):
                if index > start and nums[index] == nums[index - 1]:
                    continue  # this value already headed a branch at this depth
                path.append(nums[index])
                backtrack(index + 1)
                path.pop()

        backtrack(0)
        return result
