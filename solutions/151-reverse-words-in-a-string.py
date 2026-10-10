# 151. Reverse Words in a String
# https://leetcode.com/problems/reverse-words-in-a-string/
#
# `str.split()` with no argument splits on runs of whitespace and discards the
# leading and trailing ones, which is exactly the normalisation the statement
# asks for: the input may have leading, trailing or repeated spaces, while the
# answer may only have a single space between words. Reversing the resulting word
# list and joining it with one space is therefore the whole algorithm -- no
# manual space handling is needed, and empty words can never appear.
#
# The follow-up asks for an in-place solution: reverse the whole character array,
# then reverse each word inside it, then compact the runs of spaces with a write
# pointer. That is O(n) time and O(1) extra space on a mutable buffer; Python's
# `str` is immutable, so this file returns a new string and the buffer version
# only exists as the two-pointer oracle in the tests.
#
# Time: O(n)   Space: O(n)   (n = len(s); the word list holds at most n characters)

class Solution:
    def reverseWords(self, s: str) -> str:
        return ' '.join(reversed(s.split()))
