# 32. Longest Valid Parentheses
# https://leetcode.com/problems/longest-valid-parentheses/
#
# Keep a stack of indices whose '(' has not been matched yet, with a sentinel
# -1 at the bottom marking the position just before the current run of valid
# text. On '(' push its index. On ')' pop:
#
#   - if the stack is now empty, the ')' had no partner, so this index becomes
#     the new sentinel;
#   - otherwise the top of the stack is the unmatched '(' that bounds the
#     current valid run, and index - stack[-1] is its length.
#
# Each character is pushed and popped at most once.
#
# Time: O(n)   Space: O(n)

class Solution:
    def longestValidParentheses(self, s: str) -> int:
        stack = [-1]
        best = 0

        for index, char in enumerate(s):
            if char == '(':
                stack.append(index)
            else:
                stack.pop()
                if not stack:
                    # Unmatched ')': nothing before it can extend a valid run.
                    stack.append(index)
                else:
                    best = max(best, index - stack[-1])

        return best
