# 57. Insert Interval
# https://leetcode.com/problems/insert-interval/
#
# The input is already sorted and disjoint, so a single pass in three phases
# suffices:
#
#   1. copy every interval that ends before the new one starts;
#   2. absorb every interval that starts at or before the new one ends,
#      widening the new interval to cover them;
#   3. copy the remainder, which is already sorted and disjoint from the result.
#
# Phase 2 is the merge step, and because the input was disjoint it can only
# produce one merged interval.
#
# Time: O(n)   Space: O(n) for the output

class Solution:
    def insert(
        self, intervals: list[list[int]], newInterval: list[int]
    ) -> list[list[int]]:
        start, end = newInterval
        result: list[list[int]] = []
        index = 0
        n = len(intervals)

        while index < n and intervals[index][1] < start:
            result.append(intervals[index])
            index += 1

        while index < n and intervals[index][0] <= end:
            start = min(start, intervals[index][0])
            end = max(end, intervals[index][1])
            index += 1
        result.append([start, end])

        while index < n:
            result.append(intervals[index])
            index += 1

        return result
