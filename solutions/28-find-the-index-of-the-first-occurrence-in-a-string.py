# 28. Find the Index of the First Occurrence in a String
# https://leetcode.com/problems/find-the-index-of-the-first-occurrence-in-a-string/
#
# KMP. The naive scan restarts from scratch after every mismatch, which is
# O(n * m). Instead, precompute the longest proper prefix of needle that is
# also a suffix of needle[:i] (the lps table). On a mismatch the text pointer
# never moves backwards: it falls back to lps[j - 1], which is exactly the
# amount of the current match that can be reused. Every text character is then
# consumed once, so the search is linear.
#
# Time: O(n + m)   Space: O(m) for the lps table

class Solution:
    def strStr(self, haystack: str, needle: str) -> int:
        if not needle:
            return 0

        m = len(needle)
        lps = [0] * m
        length = 0
        i = 1
        while i < m:
            if needle[i] == needle[length]:
                length += 1
                lps[i] = length
                i += 1
            elif length:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1

        i = j = 0
        while i < len(haystack):
            if haystack[i] == needle[j]:
                i += 1
                j += 1
                if j == m:
                    return i - j
            elif j:
                j = lps[j - 1]
            else:
                i += 1

        return -1
