# 43. Multiply Strings
# https://leetcode.com/problems/multiply-strings/
#
# Grade-school long multiplication on digit arrays. Every digit pair contributes
# to one position of a len(num1) + len(num2) accumulator; products are summed
# first and a single right-to-left pass then resolves all carries, which avoids
# the error-prone interleaved carrying of the classic variant. Any position
# holds at most 9 * 9 * 200 = 16200 before the carry pass.
#
# Nothing is converted to an integer: digits are read with ord and written back
# the same way.
#
# Time: O(n * m)   Space: O(n + m)

class Solution:
    def multiply(self, num1: str, num2: str) -> str:
        if num1 == '0' or num2 == '0':
            return '0'

        n, m = len(num1), len(num2)
        digits = [0] * (n + m)

        for i in range(n - 1, -1, -1):
            a = ord(num1[i]) - ord('0')
            for j in range(m - 1, -1, -1):
                digits[i + j + 1] += a * (ord(num2[j]) - ord('0'))

        for position in range(len(digits) - 1, 0, -1):
            carry, digits[position] = divmod(digits[position], 10)
            digits[position - 1] += carry

        start = 0
        while digits[start] == 0:
            start += 1

        return ''.join(chr(ord('0') + d) for d in digits[start:])
