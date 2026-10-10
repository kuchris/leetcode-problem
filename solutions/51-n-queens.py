# 51. N-Queens
# https://leetcode.com/problems/n-queens/
#
# Place one queen per row, so only the column and the two diagonals can
# conflict. A queen at (row, col) attacks the diagonal row - col and the
# anti-diagonal row + col, so three sets make each candidate square an O(1)
# check and let the search skip whole subtrees instead of testing every pair.
#
# Time: O(n!) upper bound, far less with the conflict pruning   Space: O(n)

class Solution:
    def solveNQueens(self, n: int) -> list[list[str]]:
        results: list[list[str]] = []
        placement: list[int] = []  # column chosen for each row
        columns: set[int] = set()
        diagonals: set[int] = set()      # row - col
        anti_diagonals: set[int] = set()  # row + col

        def backtrack(row: int) -> None:
            if row == n:
                results.append([
                    '.' * col + 'Q' + '.' * (n - col - 1) for col in placement
                ])
                return

            for col in range(n):
                if col in columns or (row - col) in diagonals or (row + col) in anti_diagonals:
                    continue

                columns.add(col)
                diagonals.add(row - col)
                anti_diagonals.add(row + col)
                placement.append(col)

                backtrack(row + 1)

                placement.pop()
                columns.discard(col)
                diagonals.discard(row - col)
                anti_diagonals.discard(row + col)

        backtrack(0)
        return results
