# 58. Length of Last Word
# https://leetcode.com/problems/length-of-last-word/
#
# Scan backwards from the end: skip the trailing spaces, then count characters
# until the next space or the start of the string. That visits only the tail of
# the input and needs no split, so no extra list is allocated.
#
# Time: O(n)   Space: O(1)

class Solution:
    def lengthOfLastWord(self, s: str) -> int:
        index = len(s) - 1

        while index >= 0 and s[index] == ' ':
            index -= 1

        length = 0
        while index >= 0 and s[index] != ' ':
            length += 1
            index -= 1

        return length
