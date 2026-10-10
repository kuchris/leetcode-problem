# 89. Gray Code
# https://leetcode.com/problems/gray-code/
#
# The reflected binary code has the closed form g(i) = i ^ (i >> 1). Two facts
# make it a valid n-bit sequence for i = 0 .. 2^n - 1:
#
#   - g is injective on [0, 2^n): if i ^ (i >> 1) == j ^ (j >> 1), the highest
#     differing bit of i and j would have to cancel, which it cannot because the
#     shift only moves bits downward. So the 2^n outputs are exactly 0..2^n - 1.
#   - Consecutive indices i and i+1 differ in the trailing run of 1s of i plus
#     one bit; i ^ (i+1) is the lowest set bit of i+1, call it b. Then
#     g(i) ^ g(i+1) = b ^ (b << 1) ... and that pair of bits is exactly what the
#     two terms flip, leaving a single differing bit. The same argument with
#     i = 2^n - 1 wrapping to 0 shows the cyclic pair also differs by one bit,
#     since g(2^n - 1) = 2^(n-1) ... 0 and g(0) = 0 differ only in the top bit.
#
# Time: O(2^n)   Space: O(1) beyond the returned list

class Solution:
    def grayCode(self, n: int) -> list[int]:
        return [value ^ (value >> 1) for value in range(1 << n)]
