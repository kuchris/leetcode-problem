-- 182. Duplicate Emails
-- https://leetcode.com/problems/duplicate-emails/
--
-- Group the rows by email and keep the groups holding more than one row. The
-- grouping key is the column being reported, so every email comes out exactly
-- once and no DISTINCT is needed even when it appears five times.
--
-- PostgreSQL groups NULL keys together, so several NULL emails would be reported
-- as a single NULL row too. The statement's Person.email holds no NULLs, so that
-- never arises against the judge's data; it is asserted locally because it is a
-- real property of the grouping reading.
--
-- Time: O(n log n) to group and count, O(n) to scan. Space: O(n) for the groups.
SELECT email AS "Email"
FROM Person
GROUP BY email
HAVING COUNT(*) > 1;
