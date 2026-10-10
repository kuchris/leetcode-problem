# 131. Palindrome Partitioning
# https://leetcode.com/problems/palindrome-partitioning/
#
# Backtracking over cut positions: `backtrack(start)` extends the partition
# currently held in `path` by every palindromic piece s[start:end], and reports a
# complete partition once start reaches the end of the string.
#
# Whether a substring is a palindrome is precomputed for all O(n^2) substrings
# with an interval DP. s[i:j] is a palindrome exactly when s[i] == s[j] and
# either the gap is shorter than two characters or s[i+1:j-1] already is one, so
# filling the table by decreasing left end makes every lookup O(1) instead of
# O(n) slicing.
#
# Invariant: at the recursion depth for `start`, `path` holds palindromic pieces
# that exactly cover s[:start] in order. A partial cover is therefore never
# extended with a piece that would leave a gap, and every complete cover is
# produced exactly once because each choice of piece is tried at exactly one
# depth.
#
# Time: O(n^2 + n * 2^(n-1))   Space: O(n^2)   (n = len(s); the recursion tree
# has one node per prefix of a palindromic partition, at most 2^(n-1) partitions)

class Solution:
    def partition(self, s: str) -> list[list[str]]:
        n = len(s)

        is_palindrome = [[False] * n for _ in range(n)]
        for i in range(n - 1, -1, -1):
            for j in range(i, n):
                is_palindrome[i][j] = s[i] == s[j] and (j - i < 2 or is_palindrome[i + 1][j - 1])

        results: list[list[str]] = []
        path: list[str] = []

        def backtrack(start: int) -> None:
            if start == n:
                results.append(path.copy())
                return
            for end in range(start + 1, n + 1):
                if is_palindrome[start][end - 1]:
                    path.append(s[start:end])
                    backtrack(end)
                    path.pop()

        backtrack(0)
        return results
