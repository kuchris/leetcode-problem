# 164. Maximum Gap
# https://leetcode.com/problems/maximum-gap/
#
# Pigeonhole bucketing, which reaches the answer in one pass without sorting:
#
#   - With n values and n - 1 consecutive gaps summing to range = max - min, the
#     largest gap is at least ceil(range / (n - 1)). Call that `bucket_size`.
#   - Spread the values over buckets of that width, so there are at most n of
#     them. Two values inside one bucket differ by less than bucket_size, which
#     is at most the answer, so a same-bucket pair can never be *the* maximum
#     gap; the answer is realised between a bucket's maximum and the next
#     non-empty bucket's minimum.
#   - Keep only each bucket's min and max, then scan the buckets in order,
#     carrying the previous non-empty bucket's maximum.
#
# Invariant: after the scan, `previous` is the largest value seen in any earlier
# bucket, so each non-empty bucket contributes exactly the gap
# (bucket min - previous), and the greatest of those is the greatest gap between
# successive values of the sorted array. Equal values give range 0 and therefore
# 0 up front; fewer than two values return 0 as the statement requires.
#
# Time: O(n)   Space: O(n)

class Solution:
    def maximumGap(self, nums: list[int]) -> int:
        size = len(nums)
        if size < 2:
            return 0

        lowest, highest = min(nums), max(nums)
        if lowest == highest:
            return 0

        # Ceiling division: -(lowest - highest) // (size - 1) == ceil(range / (n-1)).
        bucket_size = max(1, -((lowest - highest) // (size - 1)))
        bucket_count = (highest - lowest) // bucket_size + 1

        bucket_min = [None] * bucket_count
        bucket_max = [None] * bucket_count
        for value in nums:
            index = (value - lowest) // bucket_size
            if bucket_min[index] is None:
                bucket_min[index] = value
                bucket_max[index] = value
            else:
                if value < bucket_min[index]:
                    bucket_min[index] = value
                if value > bucket_max[index]:
                    bucket_max[index] = value

        best = 0
        previous = lowest  # bucket 0 holds `lowest`, so this seeds the scan
        for index in range(bucket_count):
            if bucket_min[index] is None:
                continue
            gap = bucket_min[index] - previous
            if gap > best:
                best = gap
            previous = bucket_max[index]

        return best
