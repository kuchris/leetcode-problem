# 69. Sqrt(x)
# https://leetcode.com/problems/sqrtx/
#
# Binary search the largest integer whose square does not exceed x. The
# predicate mid * mid <= x is monotone in mid, so the search is valid, and it
# converges on the floor of the square root. Python's arbitrary-precision
# integers mean mid * mid cannot overflow, so no floating point or built-in
# exponent function is involved.
#
# Time: O(log x)   Space: O(1)

class Solution:
    def mySqrt(self, x: int) -> int:
        low, high = 0, x

        while low <= high:
            mid = (low + high) // 2
            if mid * mid <= x:
                low = mid + 1
            else:
                high = mid - 1

        return high
