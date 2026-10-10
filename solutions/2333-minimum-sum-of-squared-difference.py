# @lc app=leetcode id=2333 lang=python3
# Daily Challenge: 2026-10-10
# https://leetcode.com/problems/minimum-sum-of-squared-difference/

# @lc code=start
class Solution:
    def minSumSquareDiff(
        self, nums1: list[int], nums2: list[int], k1: int, k2: int
    ) -> int:
        """Minimize squared differences in O(n log(M + 1)) time, O(n) space.

        Either array can reduce an absolute difference by one, so the total
        budget is k1 + k2. Reducing a difference d saves 2*d - 1: always reduce
        the largest differences first. Binary search batches these reductions
        by finding the smallest affordable upper bound on the differences.
        """
        differences = [abs(a - b) for a, b in zip(nums1, nums2)]
        budget = k1 + k2
        if budget >= sum(differences):
            return 0

        low, high = 0, max(differences)
        while low < high:
            cap = (low + high) // 2
            cost = sum(d - cap for d in differences if d > cap)
            if cost <= budget:
                high = cap
            else:
                low = cap + 1

        cap = low
        remaining = budget
        answer = 0
        for difference in differences:
            if difference > cap:
                remaining -= difference - cap
                difference = cap
            answer += difference * difference

        # Minimality of cap guarantees fewer leftover operations than entries
        # at cap. Lower that many entries from cap to cap - 1.
        return answer - remaining * (2 * cap - 1)
# @lc code=end
