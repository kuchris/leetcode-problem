# 15. 3Sum
# https://leetcode.com/problems/3sum/
#
# Sort first, then fix the smallest element nums[i] and solve the remaining
# two-sum with converging pointers. On a sorted array, a sum that is too small
# can only be raised by advancing the left pointer, and a sum that is too large
# can only be lowered by retreating the right pointer, so each (i) scan is
# linear.
#
# Duplicate triplets are prevented at the source: skip a repeated nums[i], and
# after recording a hit, advance both pointers past their repeated values.
#
# Time: O(n^2)   Space: O(1) extra (the sort is in place; output excluded)

class Solution:
    def threeSum(self, nums: list[int]) -> list[list[int]]:
        nums.sort()
        n = len(nums)
        triplets = []

        for i in range(n - 2):
            # The smallest element is already positive, so no sum can reach 0.
            if nums[i] > 0:
                break
            if i > 0 and nums[i] == nums[i - 1]:
                continue

            left, right = i + 1, n - 1
            while left < right:
                total = nums[i] + nums[left] + nums[right]
                if total < 0:
                    left += 1
                elif total > 0:
                    right -= 1
                else:
                    triplets.append([nums[i], nums[left], nums[right]])
                    left += 1
                    right -= 1
                    while left < right and nums[left] == nums[left - 1]:
                        left += 1
                    while left < right and nums[right] == nums[right + 1]:
                        right -= 1

        return triplets
