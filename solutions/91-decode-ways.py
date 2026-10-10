# 91. Decode Ways
# https://leetcode.com/problems/decode-ways/
#
# Linear DP over prefixes with two rolling values. Let dp[i] be the number of
# ways to decode s[:i], with dp[0] = 1 (the empty prefix has exactly one
# decoding). The last code word of a decoding of s[:i] is either the single
# character s[i-1] or the pair s[i-2:i], so
#
#   dp[i] = (s[i-1] != '0'            ? dp[i-1] : 0)
#         + (s[i-2] != '0' and s[i-2:i] <= "26" ? dp[i-2] : 0)
#
# A leading zero is what makes a single digit unusable ('0' has no letter), and
# the same zero rule plus the <= 26 bound is what makes a two-digit group
# unusable ('06' and '27' are not codes).
#
# Only dp[i-1] and dp[i-2] are ever read, so two variables replace the array.
#
# Time: O(n)   Space: O(1)   (n = len(s))

class Solution:
    def numDecodings(self, s: str) -> int:
        two_back, one_back = 0, 1  # dp[i-2], dp[i-1]; dp[0] = 1

        for i in range(1, len(s) + 1):
            current = 0
            if s[i - 1] != '0':
                current += one_back
            if i >= 2 and s[i - 2] != '0' and s[i - 2:i] <= '26':
                current += two_back
            two_back, one_back = one_back, current

        return one_back
