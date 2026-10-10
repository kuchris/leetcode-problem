# 64. Minimum Path Sum
# https://leetcode.com/problems/minimum-path-sum/
#
# A path may only come from above or from the left, so the cheapest cost of a
# cell is its own value plus the cheaper of those two neighbours. Processing row
# by row lets a single array hold the answers: before a cell is updated, row[j]
# still holds the value from the row above, and row[j - 1] already holds the
# value from the left.
#
# The first row and the first column have only one predecessor each, so they are
# seeded rather than minimised.
#
# Time: O(m * n)   Space: O(n)

class Solution:
    def minPathSum(self, grid: list[list[int]]) -> int:
        n = len(grid[0])
        row = [0] * n

        row[0] = grid[0][0]
        for j in range(1, n):
            row[j] = row[j - 1] + grid[0][j]

        for i in range(1, len(grid)):
            row[0] += grid[i][0]
            for j in range(1, n):
                row[j] = min(row[j], row[j - 1]) + grid[i][j]

        return row[n - 1]
