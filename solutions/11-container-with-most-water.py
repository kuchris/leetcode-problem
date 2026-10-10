# 11. Container With Most Water
# https://leetcode.com/problems/container-with-most-water/
#
# Start with the widest container and move inwards. The area is bounded by the
# shorter wall, so moving the taller side can never help: the width shrinks and
# the height cannot grow past the shorter wall that is still in place. Moving
# the shorter side is therefore the only move that can improve the answer, and
# every pair is considered by one of the two pointers.
#
# Time: O(n)   Space: O(1)

class Solution:
    def maxArea(self, height: list[int]) -> int:
        left, right = 0, len(height) - 1
        best = 0

        while left < right:
            shorter = min(height[left], height[right])
            best = max(best, shorter * (right - left))

            if height[left] < height[right]:
                left += 1
            else:
                right -= 1

        return best
