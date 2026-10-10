# 36. Valid Sudoku
# https://leetcode.com/problems/valid-sudoku/
#
# Validity is a local property: no digit may repeat within its row, its column,
# or its 3x3 box. Track one set per row, per column and per box, and reject the
# board the moment a digit is already present in any of the three. The box index
# of cell (r, c) is (r // 3) * 3 + c // 3, which numbers the nine boxes in
# reading order.
#
# Time: O(1)  (exactly 81 cells)   Space: O(1)

class Solution:
    def isValidSudoku(self, board: list[list[str]]) -> bool:
        rows = [set() for _ in range(9)]
        columns = [set() for _ in range(9)]
        boxes = [set() for _ in range(9)]

        for r in range(9):
            for c in range(9):
                value = board[r][c]
                if value == '.':
                    continue

                box = (r // 3) * 3 + c // 3
                if value in rows[r] or value in columns[c] or value in boxes[box]:
                    return False

                rows[r].add(value)
                columns[c].add(value)
                boxes[box].add(value)

        return True
