# 22. Generate Parentheses
# https://leetcode.com/problems/generate-parentheses/
#
# Build the string left to right, only ever making a choice that can still be
# completed: add '(' while fewer than n have been used, and add ')' only while
# it would not exceed the number of '(' already placed. Those two rules keep
# every prefix balanced-prefix-valid, so no branch needs to be discarded after
# the fact and the search tree has exactly one leaf per valid string.
#
# Time: O(4^n / sqrt(n)) — the n-th Catalan number of results, each of length 2n
# Space: O(n) recursion depth (excluding the output)

class Solution:
    def generateParenthesis(self, n: int) -> list[str]:
        results: list[str] = []

        def build(prefix: str, opened: int, closed: int) -> None:
            if len(prefix) == 2 * n:
                results.append(prefix)
                return
            if opened < n:
                build(prefix + '(', opened + 1, closed)
            if closed < opened:
                build(prefix + ')', opened, closed + 1)

        build('', 0, 0)
        return results
