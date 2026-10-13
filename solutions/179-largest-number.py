# 179. Largest Number
# https://leetcode.com/problems/largest-number/
#
# For two numbers a and b, a belongs before b exactly when
# str(a) + str(b) > str(b) + str(a): both orders use the same digits, so only
# the pair's relative order decides which concatenation is larger. That relation
# is a total order (it is transitive), so sorting with it orders the whole list
# into the arrangement whose concatenation is maximal.
#
# `cmp_to_key` adapts the comparator to `list.sort`. Leading zeros are stripped
# at the end, so [0, 0] answers "0" rather than "00"; a nonzero number always
# precedes a zero under this comparator, so no real digit is ever stripped.
#
# Time: O(n log n * L)   Space: O(n * L)
# (L is the longest digit count; each comparison concatenates two strings.)

from functools import cmp_to_key


class Solution:
    def largestNumber(self, nums: list[int]) -> str:
        texts = [str(num) for num in nums]

        def compare(left: str, right: str) -> int:
            if left + right > right + left:
                return -1
            if left + right < right + left:
                return 1
            return 0

        texts.sort(key=cmp_to_key(compare))
        return ''.join(texts).lstrip('0') or '0'
