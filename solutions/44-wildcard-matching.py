# 44. Wildcard Matching
# https://leetcode.com/problems/wildcard-matching/
#
# Greedy scan with a single remembered star. The text pointer only moves
# forward:
#
#   - '?' or a matching letter consumes one character of each;
#   - '*' is remembered (its position and the text position it started at) and
#     matched against the empty string first;
#   - on any other mismatch, backtrack to the last star and let it swallow one
#     more character. If there is no star to fall back on, the match fails.
#
# Because the text pointer never rewinds past a star's start more than once per
# character, this is linear in practice and O(n * m) in the worst case, without
# the O(n * m) table that a DP would need.
#
# Time: O(n * m) worst case   Space: O(1)

class Solution:
    def isMatch(self, s: str, p: str) -> bool:
        s_index = p_index = 0
        star = -1
        star_match = 0

        while s_index < len(s):
            if p_index < len(p) and (p[p_index] == '?' or p[p_index] == s[s_index]):
                s_index += 1
                p_index += 1
            elif p_index < len(p) and p[p_index] == '*':
                star = p_index
                star_match = s_index
                p_index += 1
            elif star != -1:
                # Let the last star consume one more character.
                star_match += 1
                s_index = star_match
                p_index = star + 1
            else:
                return False

        # Any remaining pattern must consist only of stars.
        while p_index < len(p) and p[p_index] == '*':
            p_index += 1

        return p_index == len(p)
