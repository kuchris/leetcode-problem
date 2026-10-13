# 165. Compare Version Numbers
# https://leetcode.com/problems/compare-version-numbers/
#
# Split both versions on '.', then compare revision by revision; the shorter
# version is padded with "0" revisions, which is exactly what the statement's
# "treat the missing revision values as 0" rule says.
#
# Each revision is compared as a decimal number without ever converting it to a
# Python int: leading zeros are stripped, and between two zero-stripped digit
# strings the shorter one is the smaller number, and equal-length ones compare
# lexicographically (same digit ordering). That makes the comparison exact for
# arbitrarily long revisions -- no fixed-width parsing and no overflow, in
# Python or in any language that would need it.
#
# Invariant: after k comparisons every revision before index k was equal, so the
# first differing revision decides the order; exhausting both lists means the
# versions are equal.
#
# Time: O(len(version1) + len(version2))   Space: O(len(...)) for the split parts

class Solution:
    def compareVersion(self, version1: str, version2: str) -> int:
        left = version1.split('.')
        right = version2.split('.')

        for index in range(max(len(left), len(right))):
            first = left[index] if index < len(left) else '0'
            second = right[index] if index < len(right) else '0'

            first = first.lstrip('0') or '0'
            second = second.lstrip('0') or '0'

            if len(first) != len(second):
                return -1 if len(first) < len(second) else 1
            if first != second:
                return -1 if first < second else 1

        return 0
