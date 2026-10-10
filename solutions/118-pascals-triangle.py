# 118. Pascal's Triangle
# https://leetcode.com/problems/pascals-triangle/
#
# Invariant: every row starts and ends with 1, and an interior entry is the sum
# of the two entries above it, `previous[i - 1] + previous[i]`. Building rows in
# order therefore only ever needs the last finished row, so the recurrence is
# applied once per interior cell.
#
# Time: O(numRows^2)   Space: O(numRows^2) for the returned triangle
# (O(numRows) besides the output)

class Solution:
    def generate(self, numRows: int) -> list[list[int]]:
        triangle = [[1]]
        for _ in range(1, numRows):
            previous = triangle[-1]
            row = [1]
            for i in range(1, len(previous)):
                row.append(previous[i - 1] + previous[i])
            row.append(1)
            triangle.append(row)
        return triangle
