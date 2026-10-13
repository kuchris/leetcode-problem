# 171. Excel Sheet Column Number
# https://leetcode.com/problems/excel-sheet-column-number/
#
# The inverse of problem 168. A title is a bijective base-26 numeral whose digits
# A..Z have the values 1..26 (no zero digit), so it is evaluated with Horner's
# rule from the left:
#
#     value("")  = 0
#     value(p+d) = value(p) * 26 + digit(d),   digit(d) = ord(d) - ord('A') + 1.
#
# Invariant: after each character, `result` is the column number of the prefix
# read so far, so appending a digit shifts the prefix one place left (multiply by
# 26) and adds the new digit. Since A = 1, "A" = 1 and "AA" = 1 * 26 + 1 = 27 as
# required, and no special case is needed for Z or for the carry into a new
# digit.
#
# Time: O(len(columnTitle))   Space: O(1)

class Solution:
    def titleToNumber(self, columnTitle: str) -> int:
        result = 0
        for char in columnTitle:
            result = result * 26 + (ord(char) - ord('A') + 1)
        return result
