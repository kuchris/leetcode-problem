# 67. Add Binary
# https://leetcode.com/problems/add-binary/
#
# Add from the least significant end, exactly like column addition on paper.
# Each step sums the two current bits and the carry, emits the low bit and keeps
# the high bit as the next carry. The loop also runs while a carry remains, so
# "1" + "1" correctly produces an extra leading digit.
#
# Time: O(max(len(a), len(b)))   Space: O(max(len(a), len(b))) for the output

class Solution:
    def addBinary(self, a: str, b: str) -> str:
        i, j = len(a) - 1, len(b) - 1
        carry = 0
        digits = []

        while i >= 0 or j >= 0 or carry:
            total = carry
            if i >= 0:
                total += ord(a[i]) - ord('0')
                i -= 1
            if j >= 0:
                total += ord(b[j]) - ord('0')
                j -= 1
            digits.append(chr(ord('0') + (total & 1)))
            carry = total >> 1

        return ''.join(reversed(digits))
