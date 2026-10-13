-- 197. Rising Temperature
-- https://leetcode.com/problems/rising-temperature/
--
-- Self-join each row to the row recorded the day before and keep the days whose
-- temperature is higher. `p.recordDate + 1` is PostgreSQL's date-plus-integer
-- operator, which adds one day to a DATE, so only a genuinely consecutive day
-- counts as "yesterday": a row whose previous entry is a week earlier has no
-- partner and is correctly not reported. A bare LAG(temperature) with no date
-- check would compare against that older entry and report a row the statement
-- does not ask for.
--
-- id is unique and no two rows share a recordDate, so each row joins at most one
-- predecessor and cannot produce duplicates. The statement allows any output
-- order; ORDER BY only keeps the result stable for local diffing.
--
-- Time: O(n log n) for the join's date matching   Space: O(n)

SELECT w.id
FROM Weather w
JOIN Weather p ON p.recordDate + 1 = w.recordDate
WHERE w.temperature > p.temperature
ORDER BY w.id;
