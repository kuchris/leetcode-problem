# 40. Combination Sum II
# https://leetcode.com/problems/combination-sum-ii/
#
# Like Combination Sum, but each element may be used at most once, so the
# recursion advances to index + 1. Candidates can repeat in the input, so
# duplicates are suppressed at the loop level: within one call, a value equal to
# the previous value at the same depth would generate exactly the same
# combinations, because everything before it has already been considered.
#
# Time: exponential in target / min(candidates)   Space: O(n) recursion depth

class Solution:
    def combinationSum2(
        self, candidates: list[int], target: int
    ) -> list[list[int]]:
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
                if index > start and candidates[index] == candidates[index - 1]:
                    continue  # same value at the same depth: already explored
                path.append(value)
                backtrack(index + 1, remaining - value)
                path.pop()

        backtrack(0, target)
        return results
