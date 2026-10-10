# 119. Pascal's Triangle II
# https://leetcode.com/problems/pascals-triangle-ii/
#
# Row `n` holds the binomial coefficients C(n, k). Instead of adding two entries
# of the previous row, build the row from the neighbouring coefficient on its
# left, C(n, k) = C(n, k - 1) * (n - k + 1) / k. The division is exact at every
# step because the product is C(n, k) * k, so no rounding or Fraction is needed.
#
# Invariant: before iteration k, row[0..k-1] already holds row `n`'s prefix
# (starting from row[0] = 1 = C(n, 0)), and after the update row[k] = C(n, k).
# The final slot is never written by the loop and stays 1 = C(n, n).
#
# Time: O(rowIndex)   Space: O(rowIndex) for the returned row

class Solution:
    def getRow(self, rowIndex: int) -> list[int]:
        row = [1] * (rowIndex + 1)
        for k in range(1, rowIndex + 1):
            row[k] = row[k - 1] * (rowIndex - k + 1) // k
        return row
