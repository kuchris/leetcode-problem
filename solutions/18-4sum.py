# 18. 4Sum
# https://leetcode.com/problems/4sum/
#
# Generalise 3Sum: sort, fix two indices a < b, then close the remaining pair
# with converging pointers. Duplicates are skipped at both outer levels and at
# the pointer level, which is what keeps the output free of repeated
# quadruplets.
#
# Two pruning rules keep the O(n^3) worst case fast in practice: for a fixed a
# (or a, b), if even the smallest reachable sum overshoots the target, no later
# index can help and the loop can stop; if even the largest reachable sum
# undershoots, this index cannot contribute and the loop can skip ahead.
#
# Time: O(n^3) worst case, much faster with pruning   Space: O(1) extra

class Solution:
    def fourSum(self, nums: list[int], target: int) -> list[list[int]]:
        nums.sort()
        n = len(nums)
        quadruplets = []

        for a in range(n - 3):
            if a > 0 and nums[a] == nums[a - 1]:
                continue
            if nums[a] + nums[a + 1] + nums[a + 2] + nums[a + 3] > target:
                break
            if nums[a] + nums[n - 1] + nums[n - 2] + nums[n - 3] < target:
                continue

            for b in range(a + 1, n - 2):
                if b > a + 1 and nums[b] == nums[b - 1]:
                    continue
                if nums[a] + nums[b] + nums[b + 1] + nums[b + 2] > target:
                    break
                if nums[a] + nums[b] + nums[n - 1] + nums[n - 2] < target:
                    continue

                left, right = b + 1, n - 1
                while left < right:
                    total = nums[a] + nums[b] + nums[left] + nums[right]
                    if total < target:
                        left += 1
                    elif total > target:
                        right -= 1
                    else:
                        quadruplets.append(
                            [nums[a], nums[b], nums[left], nums[right]]
                        )
                        left += 1
                        right -= 1
                        while left < right and nums[left] == nums[left - 1]:
                            left += 1
                        while left < right and nums[right] == nums[right + 1]:
                            right -= 1

        return quadruplets
