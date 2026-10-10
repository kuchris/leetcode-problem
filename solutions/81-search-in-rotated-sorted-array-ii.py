# 81. Search in Rotated Sorted Array II
# https://leetcode.com/problems/search-in-rotated-sorted-array-ii/
#
# Binary search on a rotated array that may contain duplicates. At each step one
# of the two halves is still sorted, which is what lets the target be located:
#
#   - If nums[low] == nums[mid] == nums[high], both ends are indistinguishable
#     from the middle, so no half can be certified as sorted; the only sound
#     move is to drop one element from each end (they are duplicates of the
#     middle value, not the target).
#   - Else if nums[low] <= nums[mid], [low, mid] is sorted, so the target is
#     inside it exactly when nums[low] <= target < nums[mid]; otherwise it can
#     only be in the other half.
#   - Otherwise the rotation point lies in (low, mid], so [mid, high] is sorted
#     and the target is inside it exactly when nums[mid] < target <= nums[high].
#
# Every branch discards at least one element that cannot be the target, so the
# search terminates. Duplicates make the equal-ends case a one-element shrink,
# which is why the worst case degrades from O(log n) to O(n).
#
# Time: O(log n) average, O(n) worst case   Space: O(1)

class Solution:
    def search(self, nums: list[int], target: int) -> bool:
        low, high = 0, len(nums) - 1

        while low <= high:
            mid = (low + high) // 2
            if nums[mid] == target:
                return True

            if nums[low] == nums[mid] == nums[high]:
                low += 1
                high -= 1
            elif nums[low] <= nums[mid]:
                if nums[low] <= target < nums[mid]:
                    high = mid - 1
                else:
                    low = mid + 1
            else:
                if nums[mid] < target <= nums[high]:
                    low = mid + 1
                else:
                    high = mid - 1

        return False
