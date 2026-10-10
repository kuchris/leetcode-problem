# 72. Edit Distance
# https://leetcode.com/problems/edit-distance/
#
# Let distance[i][j] be the cost of turning word1[:i] into word2[:j]. The last
# characters either already match, in which case nothing is spent on them, or
# they differ, in which case one operation fixes the tail:
#
#   - replace: distance[i - 1][j - 1] + 1
#   - delete:  distance[i - 1][j] + 1
#   - insert:  distance[i][j - 1] + 1
#
# Row i depends only on row i - 1 and the cell to its left, so two rows are
# enough. Row 0 is the cost of building each prefix of word2 from nothing, i.e.
# one insert per character.
#
# Time: O(m * n)   Space: O(n)

class Solution:
    def minDistance(self, word1: str, word2: str) -> int:
        n = len(word2)
        previous = list(range(n + 1))

        for i in range(1, len(word1) + 1):
            current = [i] + [0] * n
            for j in range(1, n + 1):
                if word1[i - 1] == word2[j - 1]:
                    current[j] = previous[j - 1]
                else:
                    current[j] = 1 + min(
                        previous[j],        # delete from word1
                        current[j - 1],     # insert into word1
                        previous[j - 1],    # replace
                    )
            previous = current

        return previous[n]
