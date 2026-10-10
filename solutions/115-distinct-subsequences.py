# 115. Distinct Subsequences
# https://leetcode.com/problems/distinct-subsequences/
#
# dp[j] = number of distinct ways to form t[:j] as a subsequence of the prefix of
# s processed so far. Processing s one character at a time:
#
#     dp[j] = dp[j]                     (skip s[i-1])
#           + dp[j-1]  if s[i-1] == t[j-1]   (match s[i-1] with t[j-1])
#
# Invariant: before the update for character i, dp[j] holds the count using
# s[:i-1]; the j-loop runs downwards, so dp[j-1] is still the value from the
# previous row (i.e. s[:i-1]) while dp[j] is being updated -- which is exactly
# the "use s[i-1] after forming t[:j-1] without it" term. dp[0] = 1 (the empty
# target has one subsequence: the empty one) and never changes, and j only has to
# run up to min(i, len(t)) because longer targets cannot be formed yet.
#
# Using one row instead of an (m+1) x (n+1) table gives the O(len(t)) space
# version; plain Python ints keep the counts exact (the statement guarantees the
# answer fits in a signed 32-bit integer).
#
# Time: O(len(s) * len(t))   Space: O(len(t))

class Solution:
    def numDistinct(self, s: str, t: str) -> int:
        m, n = len(s), len(t)
        if n > m:
            return 0

        dp = [0] * (n + 1)
        dp[0] = 1
        for i in range(1, m + 1):
            char = s[i - 1]
            for j in range(min(i, n), 0, -1):
                if char == t[j - 1]:
                    dp[j] += dp[j - 1]
        return dp[n]
