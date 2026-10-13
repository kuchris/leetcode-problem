# 174. Dungeon Game
# https://leetcode.com/problems/dungeon-game/
#
# The DP has to run backwards from the princess. `need[j]` is the health the
# knight must have *before entering* the cell being processed in order to survive
# the rest of the walk; a forward DP cannot know that, because how much health is
# enough depends on the rooms still ahead of him.
#
# Princess room: leaving it with at least 1 health means entering with
# value + h >= 1, so need = max(1, 1 - value). Every other cell:
# need = max(1, min(need[right], need[down]) - value), taking the cheaper exit
# because the knight picks the better one.
#
# Invariant: when the rolling array is updated for (i, j), need[j] still holds
# the requirement of the cell below and need[j + 1] the requirement of the cell
# to the right, so min(need[j], need[j + 1]) is the cost of the best next step.
# The bottom row and the right column have only one exit each.
#
# Time: O(m * n)   Space: O(n)

class Solution:
    def calculateMinimumHP(self, dungeon: list[list[int]]) -> int:
        rows = len(dungeon)
        cols = len(dungeon[0])
        need = [0] * cols
        for i in range(rows - 1, -1, -1):
            for j in range(cols - 1, -1, -1):
                if i == rows - 1 and j == cols - 1:
                    best_next = 1
                elif i == rows - 1:
                    best_next = need[j + 1]
                elif j == cols - 1:
                    best_next = need[j]
                else:
                    best_next = min(need[j], need[j + 1])
                need[j] = max(1, best_next - dungeon[i][j])
        return need[0]
