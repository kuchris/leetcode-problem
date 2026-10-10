# 46. Permutations
# https://leetcode.com/problems/permutations/
#
# Build each permutation position by position, choosing any element that has
# not been used yet. A `used` array makes "is this element still available" an
# O(1) check, so the search tree has exactly one leaf per permutation and no
# branch is ever rejected after the fact.
#
# Time: O(n! * n)  (n! results, each of length n)   Space: O(n) recursion depth

class Solution:
    def permute(self, nums: list[int]) -> list[list[int]]:
        results: list[list[int]] = []
        path: list[int] = []
        used = [False] * len(nums)

        def backtrack() -> None:
            if len(path) == len(nums):
                results.append(path[:])
                return

            for index in range(len(nums)):
                if used[index]:
                    continue
                used[index] = True
                path.append(nums[index])
                backtrack()
                path.pop()
                used[index] = False

        backtrack()
        return results
