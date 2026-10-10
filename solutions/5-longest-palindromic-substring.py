# 5. Longest Palindromic Substring
# https://leetcode.com/problems/longest-palindromic-substring/
#
# Every palindrome is symmetric about a centre, and there are only 2n - 1
# candidate centres: n single characters (odd length) and n - 1 gaps between
# adjacent characters (even length). Expanding outwards from each centre visits
# each palindrome in O(n), so the whole scan is O(n^2).
#
# Time: O(n^2)   Space: O(1)  (only the best bounds are stored)

class Solution:
    def longestPalindrome(self, s: str) -> str:
        n = len(s)
        start, end = 0, 0  # inclusive bounds of the best palindrome so far

        def expand(left: int, right: int) -> None:
            """Grow a palindrome outwards while both ends still match."""
            nonlocal start, end
            while left >= 0 and right < n and s[left] == s[right]:
                left -= 1
                right += 1
            # The loop overshoots by one on each side, so undo that step.
            if right - left - 1 > end - start + 1:
                start, end = left + 1, right - 1

        for centre in range(n):
            expand(centre, centre)      # odd-length palindromes
            expand(centre, centre + 1)  # even-length palindromes

        return s[start:end + 1]
