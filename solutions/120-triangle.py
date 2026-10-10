# 120. Triangle
# https://leetcode.com/problems/triangle/
#
# Work bottom-up. `best[j]` is the cheapest sum of a path that starts at cell j
# of the row currently being processed and runs to the bottom; the last row is
# seeded with its own values. A cell on the row above may step to j or j + 1, so
# it costs triangle[row][j] + min(best[j], best[j + 1]).
#
# Invariant: when the loop reaches row r, best[j] for j <= len(row r) already
# holds the cheapest tail starting at cell j of row r+1 (updated in place for
# the shared indices from the previous iteration). The answer is best[0] once
# the top row has been folded in.
#
# Time: O(n^2) where n is the number of rows (O(total cells))
# Space: O(n) for the rolling array

class Solution:
    def minimumTotal(self, triangle: list[list[int]]) -> int:
        best = list(triangle[-1])
        for row in reversed(triangle[:-1]):
            for j in range(len(row)):
                best[j] = row[j] + min(best[j], best[j + 1])
        return best[0]
