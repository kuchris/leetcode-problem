# 191. Number of 1 Bits
# https://leetcode.com/problems/number-of-1-bits/
#
# Brian Kernighan's trick: `n & (n - 1)` clears the lowest set bit of n, because
# subtracting 1 borrows through the trailing zeros and flips the lowest 1 to 0.
# The loop therefore runs exactly popcount(n) times instead of once per bit
# position (32 for this input range), and it stops as soon as n reaches 0.
#
# Invariant: entering an iteration, `count` is the number of set bits already
# cleared and n holds the rest of the original bits shifted nowhere -- the
# operation removes one set bit and leaves every other bit unchanged. So when the
# loop ends, `count` is the number of set bits of the original n.
#
# The follow-up ("called many times") is answered by this same loop: it needs no
# built-in bit count, no table and O(1) space, and its work is proportional to the
# number of set bits rather than to the width of the word. A 256-entry table over
# the four bytes of the word would trade 256 words of memory for four steps.
#
# Time: O(popcount(n)), i.e. O(1) since n < 2^31   Space: O(1)

class Solution:
    def hammingWeight(self, n: int) -> int:
        count = 0
        while n:
            n &= n - 1  # clears the lowest set bit
            count += 1
        return count
