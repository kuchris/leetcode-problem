# 20. Valid Parentheses
# https://leetcode.com/problems/valid-parentheses/
#
# A single stack decides the whole string: push every opening bracket, and on a
# closing bracket require that the stack top is its matching opener. That single
# rule rejects both an unmatched closer (empty stack or wrong top) and an
# unmatched opener (stack non-empty at the end), so one left-to-right pass is
# sufficient and no backtracking is needed.
#
# Time: O(n)   Space: O(n) worst case (a string of only opening brackets)

class Solution:
    def isValid(self, s: str) -> bool:
        bracket_map = {')': '(', '}': '{', ']': '['}
        opening_brackets = set(bracket_map.values())
        stack = []

        for char in s:
            if char in opening_brackets:
                stack.append(char)
            elif char in bracket_map:
                if not stack or stack.pop() != bracket_map[char]:
                    return False

        return not stack
