# 42. Trapping Rain Water
# https://leetcode.com/problems/trapping-rain-water/
#
# The water above a bar is min(highest to its left, highest to its right) minus
# its own height. Two pointers exploit that only the smaller side matters: if
# height[left] < height[right], then some bar to the right is at least as tall as
# height[left], so the left bar's right-hand bound is already settled and its
# water can be computed from the running left maximum alone. The pointer on the
# shorter side therefore advances, and every bar is visited once.
#
# Time: O(n)   Space: O(1)

class Solution:
    def trap(self, height: list[int]) -> int:
        left, right = 0, len(height) - 1
        left_max = right_max = 0
        water = 0

        while left < right:
            if height[left] < height[right]:
                left_max = max(left_max, height[left])
                water += left_max - height[left]
                left += 1
            else:
                right_max = max(right_max, height[right])
                water += right_max - height[right]
                right -= 1

        return water
