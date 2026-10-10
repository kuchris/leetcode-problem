# 93. Restore IP Addresses
# https://leetcode.com/problems/restore-ip-addresses/
#
# Backtracking over the four octets: at each step take 1, 2 or 3 digits of the
# remaining suffix as the next octet. A segment is legal iff it is the single
# digit "0", or starts with a non-zero digit and its value is at most 255.
#
# Invariant: `segments` holds the octets already fixed for s[:start], so after
# k recursive calls the first k octets are decided and consume s[:start]. A
# completion is accepted only when the fourth octet is placed and it consumes
# exactly the whole string (start == n), which also rules out leftover digits.
#
# Counting argument that prunes to almost nothing: with `left` octets still to
# place and `digits = n - start` digits left, we need left <= digits <= 3*left,
# otherwise no split can consume the suffix. That also makes n outside [4, 12]
# answer immediately.
#
# Time: O(3^4 * n) = O(n), n = len(s) <= 20   Space: O(4) recursion depth plus
#       the returned addresses (at most 3^4 splits are ever examined)

class Solution:
    def restoreIpAddresses(self, s: str) -> list[str]:
        n = len(s)
        if n < 4 or n > 12:
            return []

        results: list[str] = []
        segments: list[str] = []

        def backtrack(start: int) -> None:
            left = 4 - len(segments)
            digits = n - start
            if digits < left or digits > 3 * left:
                return
            if left == 0:
                if start == n:
                    results.append('.'.join(segments))
                return

            value = 0
            for length in range(1, 4):
                if start + length > n:
                    break
                value = value * 10 + (ord(s[start + length - 1]) - 48)
                # "0" is the only legal octet starting with a zero, and a
                # longer segment starting with 0 is never legal either.
                if s[start] == '0' and length > 1:
                    break
                if value > 255:
                    break
                segments.append(s[start:start + length])
                backtrack(start + length)
                segments.pop()

        backtrack(0)
        return results
