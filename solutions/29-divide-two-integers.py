# 29. Divide Two Integers
# https://leetcode.com/problems/divide-two-integers/
#
# Long division in base 2, without multiplication, division or modulo. Repeatedly
# find the largest power-of-two multiple of the divisor that still fits in the
# remainder, subtract it, and set that bit in the quotient. Finding the shift is
# itself a loop, so a quotient of q bits costs O(log^2 q); Python's arbitrary
# precision means the intermediate shifts cannot overflow.
#
# The single overflowing case is INT_MIN / -1, which must saturate to INT_MAX.
#
# Time: O(log^2 n)   Space: O(1)

INT_MIN = -(2 ** 31)
INT_MAX = 2 ** 31 - 1


class Solution:
    def divide(self, dividend: int, divisor: int) -> int:
        if dividend == INT_MIN and divisor == -1:
            return INT_MAX

        negative = (dividend < 0) != (divisor < 0)
        remainder = abs(dividend)
        divisor = abs(divisor)
        quotient = 0

        while remainder >= divisor:
            shift = 0
            while remainder >= divisor << (shift + 1):
                shift += 1
            remainder -= divisor << shift
            quotient += 1 << shift

        return -quotient if negative else quotient
