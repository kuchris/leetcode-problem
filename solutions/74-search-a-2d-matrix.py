# 74. Search a 2D Matrix
# https://leetcode.com/problems/search-a-2d-matrix/
#
# The two guarantees together mean the rows form one sorted sequence: every
# value in row i is smaller than every value in row i + 1. So the matrix can be
# treated as a flat sorted array of m * n entries, and index k maps to
# matrix[k // n][k % n]. A single binary search over that range is therefore
# valid and meets the required bound.
#
# Time: O(log(m * n))   Space: O(1)

class Solution:
    def searchMatrix(self, matrix: list[list[int]], target: int) -> bool:
        columns = len(matrix[0])
        low, high = 0, len(matrix) * columns - 1

        while low <= high:
            mid = (low + high) // 2
            value = matrix[mid // columns][mid % columns]
            if value == target:
                return True
            if value < target:
                low = mid + 1
            else:
                high = mid - 1

        return False
