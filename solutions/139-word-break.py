# 139. Word Break
# https://leetcode.com/problems/word-break/
#
# dp[i] = "the prefix s[:i] can be split into dictionary words", with dp[0] = True
# for the empty prefix. A split of s[:i] ends with some dictionary word w taking
# the suffix s[i-len(w):i], and the part before it is a split of s[:i-len(w)]:
#
#     dp[i] = any(dp[i - len(w)] and s[i-len(w):i] == w for w in wordDict).
#
# Invariant: by the time the outer loop reaches i, every dp[j] with j < i is
# final, because i - len(w) < i for every non-empty word; so the recurrence only
# reads decided values. The answer is dp[len(s)].
#
# Words are bucketed by length, so position i only tests the lengths that occur
# in the dictionary (at most 20, since each word is at most 20 characters long)
# and the membership test is a set lookup instead of a scan over wordDict.
#
# Time: O(n * D)   Space: O(n) for dp plus the dictionary, where D = sum of the
#       distinct word lengths in wordDict (D <= 20 * 20 = 400); each term of the
#       inner work is one substring slice plus a set lookup

class Solution:
    def wordBreak(self, s: str, wordDict: list[str]) -> bool:
        by_length: dict[int, set[str]] = {}
        for word in wordDict:
            by_length.setdefault(len(word), set()).add(word)

        n = len(s)
        dp = [False] * (n + 1)
        dp[0] = True
        for i in range(1, n + 1):
            for length, words in by_length.items():
                start = i - length
                if start >= 0 and dp[start] and s[start:i] in words:
                    dp[i] = True
                    break
        return dp[n]
