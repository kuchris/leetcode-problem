# 77. Combinations
# https://leetcode.com/problems/combinations/
#
# Backtracking over the ascending range 1..n with no `used` set needed: every
# partial combination only appends a value strictly larger than its last one,
# so each k-subset is emitted exactly once, in increasing order.
#
# Invariant: at a call with `start`, all values below `start` are either already
# on the path or can never be used again (they would break the ascending order),
# so the loop only has to try `start..n`.
#
# Pruning: a branch that still needs `k - len(path)` values may draw them from
# the `n - value + 1` values `value..n`. The loop stops at the last `value` for
# which that is enough, i.e. value <= n - (k - len(path)) + 1, which cuts every
# suffix that cannot reach length k.
#
# Time: O(C(n, k) * k)   Space: O(k) recursion depth (output not counted)

class Solution:
    def combine(self, n: int, k: int) -> list[list[int]]:
        result: list[list[int]] = []
        path: list[int] = []

        def backtrack(start: int) -> None:
            if len(path) == k:
                result.append(path.copy())
                return
            last = n - (k - len(path)) + 1
            for value in range(start, last + 1):
                path.append(value)
                backtrack(value + 1)
                path.pop()

        backtrack(1)
        return result
