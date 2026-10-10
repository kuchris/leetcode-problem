# 97. Interleaving String
# https://leetcode.com/problems/interleaving-string/
#
# dp[i][j] = "s3[:i+j] is an interleaving of s1[:i] and s2[:j]". The last
# character of that prefix must come from s1 or from s2:
#
#     dp[i][j] = (dp[i-1][j] and s1[i-1] == s3[i+j-1])
#             or (dp[i][j-1] and s2[j-1] == s3[i+j-1]).
#
# Base cases: dp[0][0] = True, dp[i][0] = dp[i-1][0] and s1[i-1] == s3[i-1]
# (same for the first row). An immediate length check s1 + s2 == s3 in size
# rejects impossible inputs, so the answer is dp[len(s1)][len(s2)].
#
# The follow-up asks for O(len(s2)) memory: only row i-1 is needed, and the
# in-place update order j = 1..m keeps dp[j] = old row (i-1) and dp[j-1] = new
# row (i) at the right moment. dp is indexed by the shorter string, so the
# space bound is O(min(len(s1), len(s2))).
#
# Time: O(len(s1) * len(s2))   Space: O(min(len(s1), len(s2)))

class Solution:
    def isInterleave(self, s1: str, s2: str, s3: str) -> bool:
        n1, n2, n3 = len(s1), len(s2), len(s3)
        if n1 + n2 != n3:
            return False
        if n1 < n2:
            s1, s2 = s2, s1
            n1, n2 = n2, n1

        dp = [False] * (n2 + 1)
        dp[0] = True
        for j in range(1, n2 + 1):
            dp[j] = dp[j - 1] and s2[j - 1] == s3[j - 1]

        for i in range(1, n1 + 1):
            dp[0] = dp[0] and s1[i - 1] == s3[i - 1]
            for j in range(1, n2 + 1):
                from_s1 = dp[j] and s1[i - 1] == s3[i + j - 1]
                from_s2 = dp[j - 1] and s2[j - 1] == s3[i + j - 1]
                dp[j] = from_s1 or from_s2

        return dp[n2]
