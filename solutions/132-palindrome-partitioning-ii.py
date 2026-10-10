# 132. Palindrome Partitioning II
# https://leetcode.com/problems/palindrome-partitioning-ii/
#
# dp[i] is the minimum number of cuts needed for the prefix s[:i]. dp[0] = -1 is
# the sentinel that makes "the whole prefix is one palindrome" cost 0 = dp[0] + 1.
# A partition of s[:r+1] either leaves s[l:r+1] as its last piece -- which must be
# a palindrome -- and pays dp[l] + 1, so every palindromic substring s[l:r]
# relaxes dp[r+1] = min(dp[r+1], dp[l] + 1). Initialising dp[i] = i - 1 covers
# the all-single-characters partition, which always exists.
#
# Palindromic substrings are enumerated by expanding around each of the 2n - 1
# centres, so no O(n^2) table is needed. Centre c must be processed in increasing
# order for the relaxations to use final values: every palindrome that can
# improve dp[l] ends at l - 1, hence is centred strictly left of c, hence was
# expanded earlier. So when centre c relaxes dp[r+1] with dp[l], l <= c and dp[l]
# is already minimal.
#
# Time: O(n^2)   Space: O(n)   (n = len(s); each centre expands at most n steps)

class Solution:
    def minCut(self, s: str) -> int:
        n = len(s)
        dp = [i - 1 for i in range(n + 1)]

        for centre in range(n):
            left, right = centre, centre  # odd-length palindrome s[left:right+1]
            while left >= 0 and right < n and s[left] == s[right]:
                if dp[left] + 1 < dp[right + 1]:
                    dp[right + 1] = dp[left] + 1
                left -= 1
                right += 1

            left, right = centre, centre + 1  # even-length palindrome
            while left >= 0 and right < n and s[left] == s[right]:
                if dp[left] + 1 < dp[right + 1]:
                    dp[right + 1] = dp[left] + 1
                left -= 1
                right += 1

        return dp[n]
