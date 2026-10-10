# 128. Longest Consecutive Sequence
# https://leetcode.com/problems/longest-consecutive-sequence/
#
# Every consecutive run in the set of values has exactly one element with no
# predecessor (value - 1 is absent). Counting only from those starts makes the
# inner `while` walk each run once, so no value is ever visited by two runs and
# the total work stays linear even though the array is unordered and its values
# are far too sparse to sort by value range.
#
# Invariant: when the loop body runs, `value - 1` is not in the set, so `value`
# is the smallest element of its run and `length` grows to exactly that run's
# size.
#
# Time: O(n) expected   Space: O(n)   (n = len(nums); the set lookup is O(1)
# expected, and every value enters the inner loop at most once)

class Solution:
    def longestConsecutive(self, nums: list[int]) -> int:
        present = set(nums)
        best = 0

        for value in present:
            if value - 1 in present:
                continue  # not the start of a run; its start will count it

            length = 1
            while value + length in present:
                length += 1
            if length > best:
                best = length

        return best
