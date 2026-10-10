# 150. Evaluate Reverse Polish Notation
# https://leetcode.com/problems/evaluate-reverse-polish-notation/
#
# Operands are pushed onto a stack; an operator pops its right operand first and
# then its left one, combines them, and pushes the result back. Because the
# input is a valid expression, the stack ends with exactly one value.
#
# The trap is division: the statement requires truncation toward zero, while
# Python's // floors (-7 // 2 == -4, but -7 / 2 truncates to -3). The helper
# divides the magnitudes and re-applies the sign, which is exact integer
# arithmetic for every sign combination and avoids float rounding.
#
# Invariant: after each token, the stack holds the values of the operands of
# every still-open sub-expression, in the order their operators will need them.
#
# Time: O(n)   Space: O(n) for the stack

class Solution:
    def evalRPN(self, tokens: list[str]) -> int:
        stack: list[int] = []
        for token in tokens:
            if token == '+':
                right = stack.pop()
                stack.append(stack.pop() + right)
            elif token == '-':
                right = stack.pop()
                stack.append(stack.pop() - right)
            elif token == '*':
                right = stack.pop()
                stack.append(stack.pop() * right)
            elif token == '/':
                right = stack.pop()
                stack.append(self._truncate(stack.pop(), right))
            else:
                stack.append(int(token))
        return stack[-1]

    @staticmethod
    def _truncate(dividend: int, divisor: int) -> int:
        """Integer division truncated toward zero (Python's // floors)."""
        quotient = abs(dividend) // abs(divisor)
        return -quotient if (dividend < 0) != (divisor < 0) else quotient
