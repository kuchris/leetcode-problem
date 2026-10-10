# 10. Regular Expression Matching
# https://leetcode.com/problems/regular-expression-matching/
#
# Let match[i][j] mean "s[i:] matches p[j:]". The recurrence depends only on
# row i + 1 and column j + 2, so filling the table backwards from the empty
# suffixes builds every answer.
#
#   - If p[j + 1] is '*', the pair p[j:j + 2] may be dropped entirely
#     (zero repetitions, match[i][j + 2]) or, when p[j] matches s[i], it may
#     consume one character and stay put (match[i + 1][j]).
#   - Otherwise p[j] must match s[i] and the rest must match (match[i + 1][j + 1]).
#
# Row m is the empty-suffix row; match[m][n] is True and everything else in it
# is False, which correctly makes patterns such as "a*" match "".
#
# Time: O(m * n)   Space: O(m * n)

class Solution:
    def isMatch(self, s: str, p: str) -> bool:
        m, n = len(s), len(p)
        match = [[False] * (n + 1) for _ in range(m + 1)]
        match[m][n] = True

        for i in range(m, -1, -1):
            for j in range(n - 1, -1, -1):
                first_matches = i < m and (p[j] == s[i] or p[j] == '.')

                if j + 1 < n and p[j + 1] == '*':
                    # Zero repetitions, or one repetition that keeps the star.
                    match[i][j] = match[i][j + 2] or (
                        first_matches and match[i + 1][j]
                    )
                else:
                    match[i][j] = first_matches and match[i + 1][j + 1]

        return match[0][0]
