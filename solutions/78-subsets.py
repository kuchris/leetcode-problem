# 78. Subsets
# https://leetcode.com/problems/subsets/
#
# Iterative doubling: start from the power set of the empty prefix, [[]], and
# process the numbers one at a time. For each value, every subset already
# collected either excludes it (kept as is) or includes it (a copy with the
# value appended), so the list doubles.
#
# Invariant: after processing the first i numbers, `result` is exactly the power
# set of those i numbers, with each subset appearing once. The comprehension on
# the right-hand side is fully evaluated before `+=` extends the list, so the
# doubling never reads elements it is still appending.
#
# Time: O(2^n * n)   Space: O(2^n * n) for the output (O(1) working memory
# beyond it)

class Solution:
    def subsets(self, nums: list[int]) -> list[list[int]]:
        result: list[list[int]] = [[]]
        for value in nums:
            result += [subset + [value] for subset in result]
        return result
