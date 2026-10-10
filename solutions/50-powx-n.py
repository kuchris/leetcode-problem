# 50. Pow(x, n)
# https://leetcode.com/problems/powx-n/
#
# Exponentiation by squaring: halve the exponent and square the base, so the
# answer is assembled from the binary digits of n in O(log n) multiplications.
# A negative exponent defers its reciprocal to the very end, because inverting
# the base up front raises an inexact value to a huge power.
#
# Squaring alone is still not accurate enough for a base whose magnitude is
# 1 - d. Such a value is stored as a float near 1, so the relative precision of
# d is only eps / d, and the exponent multiplies that error: with d ~ 3e-9 and
# n ~ -1.7e9 the answer is off by 3e-5, past the judge's 1e-5 tolerance. Bases
# that close to +-1 therefore switch to ln|x^n| = n * ln|x|, where log1p
# recovers d without cancellation and the multiplication is exact in the
# exponent. The 1e-3 cutoff is safe under the stated constraint
# -10^4 <= x^n <= 10^4: it forces |n * ln|x|| <= 9.21, so d >= 1e-3 implies
# |n| <= 9210 and only a handful of squarings.
#
# Time: O(log |n|)   Space: O(1)

import math

NEAR_ONE = 1e-3


class Solution:
    def myPow(self, x: float, n: int) -> float:
        if abs(abs(x) - 1.0) < NEAR_ONE:
            magnitude = math.exp(n * math.log1p(abs(x) - 1.0))
            return -magnitude if x < 0 and n % 2 else magnitude

        exponent = -n if n < 0 else n
        result = 1.0
        base = x

        while exponent:
            if exponent & 1:
                result *= base
            base *= base
            exponent >>= 1

        return 1.0 / result if n < 0 else result
