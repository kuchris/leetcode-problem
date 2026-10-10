# 12. Integer to Roman
# https://leetcode.com/problems/integer-to-roman/
#
# Roman numerals are formed by appending decimal place values from highest to
# lowest, so a greedy pass over the value table is exact. The table must list
# the six subtractive forms (900, 400, 90, 40, 9, 4) alongside the seven base
# symbols; with them present, "take the largest symbol that fits" reproduces
# the canonical spelling for every value in range.
#
# Time: O(1)  (at most 13 table entries, num <= 3999)   Space: O(1)

VALUES = (
    (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
    (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
    (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I'),
)


class Solution:
    def intToRoman(self, num: int) -> str:
        parts = []
        for value, symbol in VALUES:
            count, num = divmod(num, value)
            parts.append(symbol * count)
        return ''.join(parts)
