# 101198. Longest Resilient Subarray I
# Biweekly Contest 193, Q2
# https://leetcode.com/problems/longest-resilient-subarray-i/
#
# Let a subarray hold m elements with total sum S. It is resilient exactly when
# S - a[i] is divisible by k for every position i, i.e. a[i] == S (mod k) for
# every i. Two consequences:
#
#   1. All elements of a resilient subarray share one residue r = S mod k, so a
#      candidate subarray always lies inside a maximal run of equal residues.
#   2. Summing a[i] == S over the m elements gives S == m * S (mod k), and with
#      S == r that is (m - 1) * r == 0 (mod k). Conversely, if all elements are
#      == r and (m - 1) * r == 0 (mod k), then S == m * r == r, so every
#      S - a[i] == 0 (mod k) and the subarray is resilient. That is an exact
#      characterization, not just a necessary condition.
#
# (m - 1) * r == 0 (mod k) holds iff (m - 1) is a multiple of d = k / gcd(r, k),
# so valid lengths of a residue-r run are 1, 1 + d, 1 + 2d, ... Note r == 0
# gives d == 1: a run of multiples of k is resilient at every length, and length
# 1 is always valid, which keeps the answer at least 1.
#
# So one pass over maximal equal-residue runs suffices: for a run of length L
# with residue r, the longest resilient subarray inside it is
# L - ((L - 1) mod d).
#
# Time: O(n)   Space: O(1)

from math import gcd


class Solution:
    def resilientSubarray(self, nums: list[int], k: int) -> int:
        best = 1  # a single element is always resilient
        residue = nums[0] % k
        length = 1
        for index in range(1, len(nums)):
            value = nums[index]
            current = value % k
            if current == residue:
                length += 1
            else:
                best = max(best, self._run_best(length, residue, k))
                residue, length = current, 1
        return max(best, self._run_best(length, residue, k))

    @staticmethod
    def _run_best(length: int, residue: int, k: int) -> int:
        """Longest valid length inside a run of ``length`` equal residues."""
        step = k // gcd(residue, k)
        return length - (length - 1) % step
