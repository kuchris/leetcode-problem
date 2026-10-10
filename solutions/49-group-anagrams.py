# 49. Group Anagrams
# https://leetcode.com/problems/group-anagrams/
#
# Two words are anagrams exactly when they have the same letter multiset, so
# the multiset is a valid dictionary key. Counting the 26 letters costs O(k)
# for a word of length k, which beats the O(k log k) of sorting each word, and
# the tuple of counts is hashable.
#
# Time: O(total characters)   Space: O(total characters)

class Solution:
    def groupAnagrams(self, strs: list[str]) -> list[list[str]]:
        groups: dict[tuple[int, ...], list[str]] = {}

        for word in strs:
            counts = [0] * 26
            for char in word:
                counts[ord(char) - ord('a')] += 1
            groups.setdefault(tuple(counts), []).append(word)

        return list(groups.values())
