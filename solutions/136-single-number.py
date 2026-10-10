# 136. Single Number
# https://leetcode.com/problems/single-number/
#
# XOR folding. Two properties of XOR are all that is needed:
#
#   - x ^ x == 0, so every value that appears twice cancels itself out no matter
#     where it sits in the array (XOR is commutative and associative);
#   - x ^ 0 == x, so what survives is exactly the value with no partner.
#
# Invariant: after processing a prefix, the accumulator is the XOR of that prefix,
# which equals the XOR of the prefix's unpaired values. At the end that is the
# single element.
#
# Time: O(n)   Space: O(1)

class Solution:
    def singleNumber(self, nums: list[int]) -> int:
        result = 0
        for value in nums:
            result ^= value
        return result
