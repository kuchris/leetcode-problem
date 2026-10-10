# 16. 3Sum Closest
# https://leetcode.com/problems/3sum-closest/
#
# Same sorted two-pointer sweep as 3Sum, but instead of demanding an exact zero
# the sweep records whichever sum is nearest the target. Because the pointers
# only ever move toward each other, every candidate triple is examined once.
#
# Time: O(n^2)   Space: O(1) extra (the sort is in place)

class Solution:
    def threeSumClosest(self, nums: list[int], target: int) -> int:
        nums.sort()
        n = len(nums)
        best = nums[0] + nums[1] + nums[2]

        for i in range(n - 2):
            left, right = i + 1, n - 1
            while left < right:
                total = nums[i] + nums[left] + nums[right]

                if abs(total - target) < abs(best - target):
                    best = total
                if total == target:
                    return target

                # Move the pointer that can close the remaining gap.
                if total < target:
                    left += 1
                else:
                    right -= 1

        return best
