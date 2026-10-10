# 14. Longest Common Prefix
# https://leetcode.com/problems/longest-common-prefix/
#
# Seed the answer with the first string and shrink it until it is a prefix of
# every other string. The prefix only ever gets shorter, so across the whole
# scan it is trimmed at most len(strs[0]) times, and each check is a prefix
# comparison rather than a full string comparison.
#
# Time: O(S) where S is the total number of characters in all strings
# Space: O(1) extra (the prefix is a slice of an existing string)

class Solution:
    def longestCommonPrefix(self, strs: list[str]) -> str:
        if not strs:
            return ""

        prefix = strs[0]
        for s in strs[1:]:
            while not s.startswith(prefix):
                prefix = prefix[:-1]
                if not prefix:
                    return ""

        return prefix
