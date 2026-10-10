# 87. Scramble String
# https://leetcode.com/problems/scramble-string/
#
# Top-down interval recursion. `scramble(i, j, length)` answers "is the block
# s2[j : j + length] a scramble of s1[i : i + length]?".
#
# Base: a block of one character is a scramble of itself only.
# Step: the top-level split of s1's block is at some cut in 1..length-1, giving
# x = s1[i : i+cut] and y = s1[i+cut : i+length]. The algorithm either keeps the
# order (s2's block is scramble(x) followed by scramble(y)) or swaps it (scramble(y)
# followed by scramble(x)), and each part recurses independently. Every scramble
# arises from exactly such a split at the root, so trying all cuts is complete.
#
# Pruning: a scramble cannot change the character multiset, so a block that is
# not an anagram of its partner is rejected before any splitting. Results are
# memoised on (i, j, length); the pruning makes most states fail in O(length log
# length) instead of branching.
#
# Time: O(n^4) worst case (memoised states x splits, plus the anagram checks),
#       far less in practice because of the anagram prune
# Space: O(n^3) memo entries plus O(n) recursion depth

class Solution:
    def isScramble(self, s1: str, s2: str) -> bool:
        n = len(s1)
        memo: dict[tuple[int, int, int], bool] = {}

        def scramble(i: int, j: int, length: int) -> bool:
            """Is s2[j:j+length] a scramble of s1[i:i+length]?"""
            if length == 1:
                return s1[i] == s2[j]

            key = (i, j, length)
            cached = memo.get(key)
            if cached is not None:
                return cached

            if sorted(s1[i:i + length]) != sorted(s2[j:j + length]):
                memo[key] = False
                return False

            for cut in range(1, length):
                # Keep the order: x in front of y.
                if scramble(i, j, cut) and scramble(i + cut, j + cut, length - cut):
                    memo[key] = True
                    return True
                # Swap the halves: y in front of x.
                if scramble(i, j + length - cut, cut) and scramble(i + cut, j, length - cut):
                    memo[key] = True
                    return True

            memo[key] = False
            return False

        return scramble(0, 0, n)
