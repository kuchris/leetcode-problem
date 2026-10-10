# 8. String to Integer (atoi)
# https://leetcode.com/problems/string-to-integer-atoi/
#
# Walk the string once in the order the statement prescribes: skip leading
# whitespace, consume at most one sign, then accumulate digits. Accumulation
# stops at the first non-digit, and the result is clamped to the signed 32-bit
# range.
#
# All ASCII whitespace is skipped, matching C's atoi; the statement only shows
# a space, but accepting the wider set cannot break a space-only test case.
#
# The digit test is the explicit range check '0' <= c <= '9' rather than
# str.isdigit(), which also accepts non-ASCII digits such as superscripts.
#
# Time: O(n)   Space: O(1)

WHITESPACE = ' \t\n\r\v\f'


class Solution:
    def myAtoi(self, s: str) -> int:
        index, n = 0, len(s)

        while index < n and s[index] in WHITESPACE:
            index += 1

        sign = 1
        if index < n and s[index] in '+-':
            sign = -1 if s[index] == '-' else 1
            index += 1

        value = 0
        while index < n and '0' <= s[index] <= '9':
            value = value * 10 + (ord(s[index]) - ord('0'))
            index += 1

        value *= sign
        limit = 2 ** 31
        if value < -limit:
            return -limit
        if value > limit - 1:
            return limit - 1
        return value
