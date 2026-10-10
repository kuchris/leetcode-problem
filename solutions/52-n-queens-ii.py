# 52. N-Queens II
# https://leetcode.com/problems/n-queens-ii/
#
# The same row-by-row search as N-Queens, but the three conflict sets are held
# as bitmasks and shifted instead of recomputed: when a queen occupies bit b of
# row r, its diagonal attack reaches bit b + 1 in row r + 1 (a left shift) and
# its anti-diagonal reaches bit b - 1 (a right shift). The free squares of the
# next row are therefore a single AND-NOT, and the lowest set bit enumerates the
# candidates.
#
# Only the count is needed, so no board is ever built.
#
# Time: O(n!) upper bound, far less with the conflict pruning   Space: O(n)

class Solution:
    def totalNQueens(self, n: int) -> int:
        full = (1 << n) - 1
        count = 0

        def backtrack(columns: int, diagonals: int, anti_diagonals: int) -> None:
            nonlocal count
            if columns == full:
                count += 1
                return

            available = ~(columns | diagonals | anti_diagonals) & full
            while available:
                bit = available & -available
                available ^= bit
                backtrack(
                    columns | bit,
                    (diagonals | bit) << 1,
                    (anti_diagonals | bit) >> 1,
                )

        backtrack(0, 0, 0)
        return count
