# 96. Unique Binary Search Trees
# https://leetcode.com/problems/unique-binary-search-trees/
#
# The count of BSTs over n distinct ordered values is the Catalan number, by
# the same root decomposition as problem 95: choosing root rank r + 1 splits the
# remaining n - 1 values into a left part of size r and a right part of size
# n - 1 - r, so
#
#     dp[n] = sum over r = 0 .. n-1 of dp[r] * dp[n - 1 - r],   dp[0] = 1.
#
# Invariant: before iteration `nodes`, dp[k] already holds the number of BSTs
# on k values for every k < nodes, so every term of the sum is a finished
# value; the sum is a product of independent choices (left shape x right shape).
#
# Time: O(n^2)   Space: O(n)   (n <= 19, dp[19] = 1767263190)

class Solution:
    def numTrees(self, n: int) -> int:
        dp = [0] * (n + 1)
        dp[0] = 1
        for nodes in range(1, n + 1):
            total = 0
            for left in range(nodes):
                total += dp[left] * dp[nodes - 1 - left]
            dp[nodes] = total
        return dp[n]
