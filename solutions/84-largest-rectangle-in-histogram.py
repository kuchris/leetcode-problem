# 84. Largest Rectangle in Histogram
# https://leetcode.com/problems/largest-rectangle-in-histogram/
#
# Every maximal rectangle can be described by the shortest bar it spans: if that
# bar is heights[i], the widest rectangle using it as the minimum extends left to
# the previous strictly shorter bar and right to the next strictly shorter bar.
# So it is enough to find, for each bar, that maximal span.
#
# A monotonic stack of indices with non-decreasing heights gives all of them in
# one pass. Invariant: indices on the stack have increasing heights, and each is
# waiting for its next smaller bar. When a bar at `index` is not taller than the
# stack top, that top's next-smaller bar is now known, so it is popped and its
# area is bar * (index - previous_smaller - 1); after the pop, the new stack top
# is exactly that previous smaller index. A virtual bar of height 0 at
# `index == n` flushes whatever remains.
#
# Each index is pushed once and popped once.
#
# Time: O(n)   Space: O(n)   (n = len(heights); the stack holds at most n indices)

class Solution:
    def largestRectangleArea(self, heights: list[int]) -> int:
        stack: list[int] = []
        best = 0
        n = len(heights)

        for index in range(n + 1):
            height = heights[index] if index < n else 0
            while stack and heights[stack[-1]] >= height:
                bar = heights[stack.pop()]
                width = index if not stack else index - stack[-1] - 1
                if bar * width > best:
                    best = bar * width
            if index < n:
                stack.append(index)

        return best
