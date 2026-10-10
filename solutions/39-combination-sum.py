# 39. Combination Sum
# https://leetcode.com/problems/combination-sum/
#
# Depth-first search over a sorted candidate list, always continuing from the
# current index so that a candidate may be reused. Sorting enables an early
# break: once a candidate exceeds the remaining target, every later candidate
# does too.
#
# Fixing the non-decreasing order of the chosen indices is what makes each
# combination appear exactly once, so no deduplication step is needed.
#
# Time: exponential in target / min(candidates)   Space: O(target / min) depth

class Solution:
    def combinationSum(self, candidates: list[int], target: int) -> list[list[int]]:
        candidates.sort()
        results: list[list[int]] = []
        path: list[int] = []

        def backtrack(start: int, remaining: int) -> None:
            if remaining == 0:
                results.append(path[:])
                return

            for index in range(start, len(candidates)):
                value = candidates[index]
                if value > remaining:
                    break
                path.append(value)
                # `index` (not index + 1) allows unlimited reuse.
                backtrack(index, remaining - value)
                path.pop()

        backtrack(0, target)
        return results
