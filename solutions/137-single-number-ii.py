# 137. Single Number II
# https://leetcode.com/problems/single-number-ii/
#
# Bit-state automaton instead of counting bits of every position separately.
# `ones` and `twos` hold, for each bit position, whether that bit has been seen
# once or twice so far modulo three:
#
#   state (ones, twos) = (0, 0) -> 0 occurrences so far
#                        (1, 0) -> 1 occurrence
#                        (0, 1) -> 2 occurrences
#                        (0, 0) -> 3 occurrences, i.e. back to the start
#
# The two updates implement exactly that transition for every bit at once:
#
#   ones = (ones ^ value) & ~twos   -- flip the bit in `ones` unless it is
#                                      already parked in `twos`
#   twos = (twos ^ value) & ~ones   -- then the same for `twos`, using the new
#                                      `ones` so a third occurrence clears both
#
# Value bits that occur three times cancel out of `ones` entirely, so what
# remains is the single element's bits. The state is two machine words, so this
# is constant extra space and one pass. Python's arbitrary-precision integers
# keep the per-bit arithmetic exact for negative values too, since each bit
# position evolves independently.
#
# Time: O(n)   Space: O(1)

class Solution:
    def singleNumber(self, nums: list[int]) -> int:
        ones = 0
        twos = 0

        for value in nums:
            ones = (ones ^ value) & ~twos
            twos = (twos ^ value) & ~ones

        return ones
