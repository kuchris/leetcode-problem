# 37. Sudoku Solver
# https://leetcode.com/problems/sudoku-solver/
#
# Backtracking with the three constraints held as 9-bit masks, so "is digit d
# legal at (r, c)" is a single AND. Candidates are tried in the order of the
# fewest-remaining-values heuristic: always fill the empty cell that currently
# has the fewest legal digits. Cells with zero candidates fail immediately and
# cells with one candidate are forced, which prunes the search far more than a
# fixed row-major order.
#
# Time: exponential in the worst case, fast in practice with the MRV ordering
# Space: O(1)  (fixed 9x9 grid plus O(81) recursion depth)

class Solution:
    def solveSudoku(self, board: list[list[str]]) -> None:
        """Do not return anything, modify board in-place instead."""
        rows = [0] * 9
        columns = [0] * 9
        boxes = [0] * 9
        empties = []

        for r in range(9):
            for c in range(9):
                value = board[r][c]
                if value == '.':
                    empties.append((r, c))
                else:
                    bit = 1 << (ord(value) - ord('1'))
                    rows[r] |= bit
                    columns[c] |= bit
                    boxes[(r // 3) * 3 + c // 3] |= bit

        def solve() -> bool:
            # Pick the unassigned cell with the fewest legal digits.
            target = None
            fewest = 10
            for r, c in empties:
                if board[r][c] != '.':
                    continue
                used = rows[r] | columns[c] | boxes[(r // 3) * 3 + c // 3]
                remaining = 9 - bin(used).count('1')
                if remaining < fewest:
                    fewest = remaining
                    target = (r, c)
                    if remaining == 0:
                        break

            if target is None:
                return True  # every cell is filled

            r, c = target
            box = (r // 3) * 3 + c // 3
            used = rows[r] | columns[c] | boxes[box]

            for digit in range(1, 10):
                bit = 1 << (digit - 1)
                if used & bit:
                    continue

                board[r][c] = chr(ord('0') + digit)
                rows[r] |= bit
                columns[c] |= bit
                boxes[box] |= bit

                if solve():
                    return True

                rows[r] &= ~bit
                columns[c] &= ~bit
                boxes[box] &= ~bit
                board[r][c] = '.'

            return False

        solve()
