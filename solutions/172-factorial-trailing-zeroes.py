# 172. Factorial Trailing Zeroes
# https://leetcode.com/problems/factorial-trailing-zeroes/
#
# A trailing zero of n! is a factor 10 = 2 * 5, and n! contains far more factors
# of 2 than of 5, so the number of trailing zeroes equals the number of factors
# of 5 in n!. By Legendre's formula that count is
#
#     sum over k >= 1 of floor(n / 5^k),
#
# because exactly floor(n / 5^k) of the numbers 1..n contribute a k-th factor of
# five.
#
# Invariant: after the iteration for 5^k, `zeroes` is the number of factors of 5
# contributed by powers up to 5^k, and the loop stops as soon as 5^k > n, at
# which point every remaining term floor(n / 5^j) is zero. The loop runs
# O(log_5 n) times and holds only one power, so the follow-up's logarithmic time
# is met and n! is never computed (10^4! has more than 35,000 digits).
#
# Time: O(log_5 n)   Space: O(1)

class Solution:
    def trailingZeroes(self, n: int) -> int:
        zeroes = 0
        power = 5
        while power <= n:
            zeroes += n // power
            power *= 5
        return zeroes
