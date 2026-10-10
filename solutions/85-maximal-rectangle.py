# 85. Maximal Rectangle
# https://leetcode.com/problems/maximal-rectangle/
#
# Reduce each row to a 1D histogram: heights[c] is how many consecutive '1's end
# at the current row in column c. Any all-ones rectangle with its bottom edge on
# this row is exactly a rectangle in that histogram, so the answer is the best
# histogram rectangle over all rows -- 84. Largest Rectangle in Histogram applied
# once per row.
#
# Invariant: after processing row r, heights[c] equals the number of rows
# r, r-1, ... that are all '1' in column c, i.e. the height of the run of 1s
# ending at (r, c); it resets to 0 on a '0'. The monotonic stack inside each row
# finds, for every bar, the widest span in which it is the minimum, exactly as in
# problem 84.
#
# Time: O(rows * cols)   Space: O(cols)   (heights + one stack per row)

class Solution:
    def maximalRectangle(self, matrix: list[list[str]]) -> int:
        if not matrix or not matrix[0]:
            return 0

        cols = len(matrix[0])
        heights = [0] * cols
        best = 0

        for row in matrix:
            for c in range(cols):
                heights[c] = heights[c] + 1 if row[c] == '1' else 0

            stack: list[int] = []
            for index in range(cols + 1):
                current = heights[index] if index < cols else 0
                while stack and heights[stack[-1]] >= current:
                    bar = heights[stack.pop()]
                    width = index if not stack else index - stack[-1] - 1
                    if bar * width > best:
                        best = bar * width
                if index < cols:
                    stack.append(index)

        return best
