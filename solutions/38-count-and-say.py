# 38. Count and Say
# https://leetcode.com/problems/count-and-say/
#
# Build the sequence iteratively: each term is the run-length encoding of the
# previous one. A single pass over the current term finds each maximal run of
# equal digits and appends "<length><digit>". Every term is fully rewritten, so
# the cost is proportional to the total length of the terms produced, which
# grows by roughly 1.3x per step.
#
# Time: O(L) where L is the length of the n-th term   Space: O(L)

class Solution:
    def countAndSay(self, n: int) -> str:
        term = '1'

        for _ in range(n - 1):
            parts = []
            i = 0
            while i < len(term):
                j = i
                while j < len(term) and term[j] == term[i]:
                    j += 1
                parts.append(str(j - i))
                parts.append(term[i])
                i = j
            term = ''.join(parts)

        return term
