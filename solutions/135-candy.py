# 135. Candy
# https://leetcode.com/problems/candy/
#
# Each child's count has two independent lower bounds:
#
#   - the left-to-right requirement: a strictly higher rating than the previous
#     child forces one more candy than that child, so scanning left to right and
#     raising the count gives the smallest value satisfying every "> left"
#     constraint;
#   - the right-to-left requirement: symmetrically, scanning right to left and
#     taking the maximum gives the smallest value satisfying every "> right"
#     constraint.
#
# Invariant: after the left pass `candies[i]` is the exact lower bound imposed by
# the prefix ratings[0..i]; after the right pass it is the pointwise maximum of
# the two directional bounds. That vector is feasible (each constraint is
# satisfied by the bound that generated it) and it is minimal, because every
# entry is forced to be at least its bound by some chain of strictly increasing
# ratings. The answer is its sum.
#
# Time: O(n)   Space: O(n)   (n = len(ratings); the vector is the working state)

class Solution:
    def candy(self, ratings: list[int]) -> int:
        n = len(ratings)
        candies = [1] * n

        for index in range(1, n):
            if ratings[index] > ratings[index - 1]:
                candies[index] = candies[index - 1] + 1

        for index in range(n - 2, -1, -1):
            if ratings[index] > ratings[index + 1] and candies[index] <= candies[index + 1]:
                candies[index] = candies[index + 1] + 1

        return sum(candies)
