-- 180. Consecutive Numbers
-- https://leetcode.com/problems/consecutive-numbers/
--
-- A number qualifies when three consecutive rows of the id ordering all hold
-- it. The rows are read positionally with LAG rather than by comparing "id + 1",
-- because ids are only guaranteed to be unique, not contiguous: with ids 1, 5
-- and 9 holding the same value, "id + 1" sees no run at all, while the ordering
-- reading sees one.
--
-- Every row that has two predecessors of the same value marks its run, so a run
-- of n >= 3 rows is marked n - 2 times; DISTINCT collapses those marks into one
-- row per number, which is what the expected output shows. Comparing with "="
-- also means a NULL num can never mark a run, since the comparison is unknown
-- rather than true.
--
-- Time: O(n log n) to order the rows and O(n) to scan them. Space: O(n).
SELECT DISTINCT num AS "ConsecutiveNums"
FROM (
    SELECT num,
           LAG(num, 1) OVER (ORDER BY id) AS prev1,
           LAG(num, 2) OVER (ORDER BY id) AS prev2
    FROM Logs
) AS runs
WHERE prev1 = num
  AND prev2 = num;
