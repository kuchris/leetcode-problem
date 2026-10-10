# 134. Gas Station
# https://leetcode.com/problems/gas-station/
#
# One pass keeping three values:
#
#   - `total` is the whole circuit's surplus, sum(gas) - sum(cost). If it is
#     negative the trip is impossible from anywhere, so the answer is -1.
#   - `tank` is the net surplus accumulated since the current candidate `start`.
#   - When `tank` goes negative at index i, the tank on arriving at i was smaller
#     than the deficit there, and any start s in [start, i] would reach i with a
#     tank no larger than this one (it has fewer stations' worth of surplus), so
#     no station up to i can work; the next candidate is i + 1 and the tank
#     restarts from zero.
#
# Invariant: `start` is the first index not yet ruled out, and every index before
# it has been proven impossible. When `total >= 0` the surviving start is
# feasible (the classic exchange argument: the deficits ruled out above are
# exactly the ones a valid tour must cross with a surplus, and on a non-negative
# total the last surviving candidate is the unique one).
#
# Time: O(n)   Space: O(1)

class Solution:
    def canCompleteCircuit(self, gas: list[int], cost: list[int]) -> int:
        total = 0
        tank = 0
        start = 0

        for index in range(len(gas)):
            surplus = gas[index] - cost[index]
            total += surplus
            tank += surplus
            if tank < 0:
                start = index + 1
                tank = 0

        return start if total >= 0 else -1
