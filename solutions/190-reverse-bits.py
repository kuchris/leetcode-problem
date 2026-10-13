# 190. Reverse Bits
# https://leetcode.com/problems/reverse-bits/
#
# The width is fixed at 32 bits, so leading zeros of the input become trailing
# zeros of the output: every one of the 32 positions must be shifted out, not
# just the significant bits. Building the answer left to right does exactly that
# -- shift the result up, append the current lowest bit of n, then drop that bit.
#
# Invariant: before iteration i, `result` holds the reversal of the lowest i bits
# of the original n, and `n` holds the remaining 32 - i bits. After 32
# iterations every bit has been moved to position 31 - i, which is the reversal.
#
# Time: O(32) = O(1)   Space: O(1)

class Solution:
    def reverseBits(self, n: int) -> int:
        result = 0
        for _ in range(32):
            result = (result << 1) | (n & 1)
            n >>= 1
        return result
