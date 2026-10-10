# 155. Min Stack
# https://leetcode.com/problems/min-stack/
#
# Entry point: MinStack
# LeetCode judges this problem through MinStack, not Solution -- the template
# defines no Solution class, so a Solution here would never be instantiated.
#
# Two parallel stacks: `_values` holds the elements, and `_minima` holds, at the
# same height, the minimum of everything currently in `_values`. `push` appends
# value and min(value, previous minimum), so the top of `_minima` is always the
# stack minimum; `pop` removes one entry from each. Nothing is ever recomputed, so
# every operation touches a constant number of list slots.
#
# Invariant: len(_values) == len(_minima), and _minima[-1] is min(_values). Both
# parts are restored together by every push and pop, which is why popping the
# current minimum needs no search -- the previous minimum is already underneath it.
#
# Time: O(1) per operation   Space: O(n)   (n = number of elements held)

class MinStack:

    def __init__(self):
        self._values: list[int] = []
        self._minima: list[int] = []

    def push(self, value: int) -> None:
        self._values.append(value)
        if self._minima:
            self._minima.append(value if value < self._minima[-1] else self._minima[-1])
        else:
            self._minima.append(value)

    def pop(self) -> None:
        self._values.pop()
        self._minima.pop()

    def top(self) -> int:
        return self._values[-1]

    def getMin(self) -> int:
        return self._minima[-1]
