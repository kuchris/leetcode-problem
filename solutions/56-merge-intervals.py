# 56. Merge Intervals
# https://leetcode.com/problems/merge-intervals/
#
# Sorting by start time makes overlaps adjacent: once the intervals are ordered,
# an interval can only overlap the run currently being built, never one that was
# already closed. Extend the current run when the next start is within its end,
# otherwise start a new run. Touching endpoints count as overlapping, hence the
# `<=` rather than `<`.
#
# Time: O(n log n)  (the sort dominates)   Space: O(n) for the output

class Solution:
    def merge(self, intervals: list[list[int]]) -> list[list[int]]:
        merged: list[list[int]] = []

        for start, end in sorted(intervals, key=lambda interval: interval[0]):
            if merged and start <= merged[-1][1]:
                if end > merged[-1][1]:
                    merged[-1][1] = end
            else:
                merged.append([start, end])

        return merged
