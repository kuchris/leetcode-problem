-- 178. Rank Scores
-- https://leetcode.com/problems/rank-scores/
--
-- DENSE_RANK() numbers the distinct scores from the highest down and gives tied
-- scores the same number, which is precisely the "no holes between ranks" rule.
-- RANK() is the wrong function here: after a two-way tie it jumps to 3, leaving
-- the hole the statement forbids.
--
-- Invariant: every row of Scores appears exactly once, its rank is one more than
-- the number of distinct scores greater than its own, and the output is ordered by
-- score descending as the statement requires -- so the ORDER BY is part of the
-- answer, not decoration.
--
-- Time: O(n log n)   Space: O(n)   (n = number of Scores rows)

SELECT score,
       DENSE_RANK() OVER (ORDER BY score DESC) AS "rank"
FROM Scores
ORDER BY score DESC;
