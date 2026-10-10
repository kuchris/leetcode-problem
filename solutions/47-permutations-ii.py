# 47. Permutations II
# https://leetcode.com/problems/permutations-ii/
#
# Same search as Permutations, with duplicates removed at the source. Sorting
# puts equal values next to each other, and then the rule
#
#     skip nums[i] when it equals nums[i - 1] and nums[i - 1] is not in use
#
# forces equal values to be consumed strictly left to right. Two branches that
# differ only by which copy of a repeated value they took therefore collapse
# into one, and every distinct permutation is produced exactly once.
#
# Time: O(n! * n) worst case (all distinct)   Space: O(n) recursion depth

class Solution:
    def permuteUnique(self, nums: list[int]) -> list[list[int]]:
        nums.sort()
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
                if index > 0 and nums[index] == nums[index - 1] and not used[index - 1]:
                    continue  # an identical value is still available earlier
                used[index] = True
                path.append(nums[index])
                backtrack()
                path.pop()
                used[index] = False

        backtrack()
        return results
