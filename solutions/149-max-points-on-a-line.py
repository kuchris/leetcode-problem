# 149. Max Points on a Line
# https://leetcode.com/problems/max-points-on-a-line/
#
# Anchor at each point and count how many other points share a direction with
# it: two points lie on the same line through the anchor exactly when their
# difference vectors are parallel, i.e. when (dx, dy) reduces to the same
# primitive pair. Every line is counted once per anchor it passes through, and
# a line through the anchor with k other points contributes k + 1 points.
#
# Invariant: slopes maps a primitive direction to the number of points seen so
# far that lie on that ray from the anchor, and `same` counts points identical
# to the anchor (they sit on every one of those lines). Dividing dx and dy by
# gcd(|dx|, |dy|) and forcing dx > 0 (or dx == 0, dy > 0) makes opposite
# directions collapse into one key, so the comparison is exact integer
# arithmetic and never floating point.
#
# Time: O(n^2 log C) for the coordinate range C (one gcd per pair)   Space: O(n)

from math import gcd


class Solution:
    def maxPoints(self, points: list[list[int]]) -> int:
        best = 0
        for i in range(len(points)):
            x1, y1 = points[i]
            slopes: dict[tuple[int, int], int] = {}
            same = 0
            for j in range(i + 1, len(points)):
                x2, y2 = points[j]
                dx = x2 - x1
                dy = y2 - y1
                if dx == 0 and dy == 0:
                    same += 1
                    continue
                divisor = gcd(abs(dx), abs(dy))
                dx //= divisor
                dy //= divisor
                if dx < 0 or (dx == 0 and dy < 0):
                    dx = -dx
                    dy = -dy
                slopes[(dx, dy)] = slopes.get((dx, dy), 0) + 1
            longest = max(slopes.values(), default=0)
            best = max(best, longest + same + 1)
        return best
