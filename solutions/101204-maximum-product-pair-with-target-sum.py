# 101204. Maximum Product Pair With Target Sum
# Biweekly Contest 193, Q1
# https://leetcode.com/problems/maximum-product-pair-with-target-sum/
#
# A valid pair (i, j) satisfies nums[i] + nums[j] == target and nums[i] > nums[j].
# Write x = nums[i]; the complement is then forced, nums[j] == target - x, and
# the ordering constraint is exactly 2 * x > target. The product of such a pair
# is x * (target - x), a downward parabola in x with its peak at target / 2, so
# it increases as x approaches target / 2 from either side. Every valid x sits
# strictly above target / 2, so the *smallest* feasible x yields the maximum
# product -- checking all candidate values is enough, no pair enumeration.
#
# Feasibility check: 2 * x > target implies x != target - x, so the two values
# differ and any index holding target - x is automatically distinct from the
# index holding x. A value -> first index map therefore suffices.
#
# Time: O(n)   Space: O(n) for the value -> first index map

class Solution:
    def maxProductPair(self, nums: list[int], target: int) -> list[int]:
        first_index: dict[int, int] = {}
        for index, value in enumerate(nums):
            first_index.setdefault(value, index)

        # Smallest x with 2 * x > target whose complement is also in nums.
        best: int | None = None
        for value in first_index:
            if 2 * value > target and target - value in first_index:
                if best is None or value < best:
                    best = value

        if best is None:
            return [-1, -1]
        return [first_index[best], first_index[target - best]]
