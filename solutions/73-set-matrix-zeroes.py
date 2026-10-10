# 73. Set Matrix Zeroes
# https://leetcode.com/problems/set-matrix-zeroes/
#
# Constant extra space by using the first row and the first column as the
# marker storage: seeing a zero at (i, j) with i, j >= 1 records it in
# matrix[i][0] and matrix[0][j]. A second sweep zeroes every interior cell whose
# row or column marker is set.
#
# The first row and column cannot double as markers for themselves, so whether
# each originally contained a zero is captured up front in two booleans and
# applied last. Order matters: the markers must be consumed before they are
# overwritten.
#
# Time: O(m * n)   Space: O(1)

class Solution:
    def setZeroes(self, matrix: list[list[int]]) -> None:
        """Do not return anything, modify matrix in-place instead."""
        rows = len(matrix)
        columns = len(matrix[0])

        first_row_has_zero = any(matrix[0][j] == 0 for j in range(columns))
        first_column_has_zero = any(matrix[i][0] == 0 for i in range(rows))

        for i in range(1, rows):
            for j in range(1, columns):
                if matrix[i][j] == 0:
                    matrix[i][0] = 0
                    matrix[0][j] = 0

        for i in range(1, rows):
            for j in range(1, columns):
                if matrix[i][0] == 0 or matrix[0][j] == 0:
                    matrix[i][j] = 0

        if first_row_has_zero:
            for j in range(columns):
                matrix[0][j] = 0
        if first_column_has_zero:
            for i in range(rows):
                matrix[i][0] = 0
