# 50. Pow(x, n)
# https://leetcode.com/problems/powx-n/
#
# Binary exponentiation. Squaring the base while halving the exponent means the
# result is assembled from the binary digits of n, so only O(log n)
# multiplications are needed instead of n. A negative exponent is handled by
# inverting the base once, which also keeps the loop uniform.
#
# Time: O(log |n|)   Space: O(1)

class Solution:
    def myPow(self, x: float, n: int) -> float:
        if n < 0:
            x = 1.0 / x
            n = -n

        result = 1.0
        while n:
            if n & 1:
                result *= x
            x *= x
            n >>= 1

        return result
