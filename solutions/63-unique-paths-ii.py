# 63. Unique Paths II
# https://leetcode.com/problems/unique-paths-ii/
#
# The same rolling-row DP as Unique Paths, with obstacles folded in: an
# obstacle has zero ways to reach it, and a free cell sums the ways from above
# (still in row[j]) and from the left (already updated to row[j - 1]).
#
# The starting cell is special: it is seeded directly, so a blocked start gives
# zero everywhere. The j == 0 column is never summed, which correctly makes it
# reachable only by moving down.
#
# Time: O(m * n)   Space: O(n)

class Solution:
    def uniquePathsWithObstacles(self, obstacleGrid: list[list[int]]) -> int:
        n = len(obstacleGrid[0])
        row = [0] * n
        row[0] = 1 if obstacleGrid[0][0] == 0 else 0

        for i in range(len(obstacleGrid)):
            for j in range(n):
                if obstacleGrid[i][j] == 1:
                    row[j] = 0
                elif j > 0:
                    row[j] += row[j - 1]

        return row[n - 1]
