# 62. Unique Paths
# https://leetcode.com/problems/unique-paths/
#
# Every path from the top-left to the bottom-right uses exactly m - 1 downs and
# n - 1 rights, so the count is the binomial coefficient C(m + n - 2, m - 1).
# The DP below computes the same value: paths[i][j] = paths[i-1][j] +
# paths[i][j-1], and since each row only depends on the row above and the cell
# to its left, one array suffices.
#
# Time: O(m * n)   Space: O(n)

class Solution:
    def uniquePaths(self, m: int, n: int) -> int:
        # row[j] holds the number of paths to column j of the current row.
        row = [1] * n

        for _ in range(m - 1):
            for j in range(1, n):
                row[j] += row[j - 1]

        return row[n - 1]
