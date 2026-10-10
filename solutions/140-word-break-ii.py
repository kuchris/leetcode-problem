# 140. Word Break II
# https://leetcode.com/problems/word-break-ii/
#
# Every segmentation of s is enumerated from left to right: sentences(i) returns
# all sentences that cover s[i:], built by picking a dictionary word matching a
# prefix of s[i:] and appending it in front of every sentence of the remainder.
#
# Invariant: memo[i] holds exactly the list of sentences for s[i:] once computed,
# so the recursion is a memoised enumeration of the *result set* rather than a
# boolean decision problem, and sentences(n) = [''] is the empty tail that ends
# the recursion. reachable[i] ("s[i:] can be segmented at all") is computed
# backwards first and used as a prune, so branches that cannot reach the end are
# never expanded -- without it, inputs like "aaaa...a" with several short words
# would waste exponential time on dead suffixes.
#
# Time: O(n * D + S)   Space: O(n + S), where D = sum of the distinct word
#       lengths (<= 100) and S = total size of the returned answer, which the
#       statement bounds by 10^5 characters

class Solution:
    def wordBreak(self, s: str, wordDict: list[str]) -> list[str]:
        by_length: dict[int, set[str]] = {}
        for word in wordDict:
            by_length.setdefault(len(word), set()).add(word)

        n = len(s)
        reachable = [False] * (n + 1)
        reachable[n] = True
        for i in range(n - 1, -1, -1):
            for length, words in by_length.items():
                if (i + length <= n and reachable[i + length]
                        and s[i:i + length] in words):
                    reachable[i] = True
                    break

        memo: dict[int, list[str]] = {}

        def sentences(i: int) -> list[str]:
            if i == n:
                return ['']
            if i in memo:
                return memo[i]
            out: list[str] = []
            for length, words in by_length.items():
                end = i + length
                if end <= n and reachable[end] and s[i:end] in words:
                    word = s[i:end]
                    for tail in sentences(end):
                        out.append(word if not tail else word + ' ' + tail)
            memo[i] = out
            return out

        return sentences(0)
