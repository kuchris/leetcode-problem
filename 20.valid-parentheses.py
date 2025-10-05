#
# @lc app=leetcode id=20 lang=python3
#
# [20] Valid Parentheses
#

# @lc code=start
class Solution:
    def isValid(self, s: str) -> bool:
        """
        Validates if parentheses in string follow correct order rules.
        Uses stack-based approach for O(n) time complexity.
        """
        # Stack-based approach using hash mapping
        stack = []
        # Dictionary mapping closing to opening brackets
        bracket_map = {')': '(', '}': '{', ']': '['}
        opening_brackets = set(bracket_map.values())
        
        for char in s:
            # If character is opening bracket, push to stack
            if char in opening_brackets:
                stack.append(char)
            # If character is closing bracket
            elif char in bracket_map:
                # Check if stack is empty or mismatch
                if not stack or stack.pop() != bracket_map[char]:
                    return False
        
        # Return True if stack is empty (all brackets matched)
        return not stack
# @lc code=end