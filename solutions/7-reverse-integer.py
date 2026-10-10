# 7. Reverse Integer
# https://leetcode.com/problems/reverse-integer/
#
# Peel digits off the low end with divmod and push them onto the result. Python
# integers are arbitrary precision, so the "no 64-bit storage" restriction is
# satisfied trivially; only the final range check matters. Values outside the
# signed 32-bit range collapse to 0.
#
# Time: O(log|x|)  (one step per digit)   Space: O(1)

class Solution:
    def reverse(self, x: int) -> int:
        sign = -1 if x < 0 else 1
        remaining = abs(x)
        result = 0

        while remaining:
            remaining, digit = divmod(remaining, 10)
            result = result * 10 + digit

        result *= sign
        return result if -(2 ** 31) <= result <= 2 ** 31 - 1 else 0
