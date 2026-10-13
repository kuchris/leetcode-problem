-- 176. Second Highest Salary
-- https://leetcode.com/problems/second-highest-salary/
--
-- The trap is the shape of the result when there is no second highest salary: an
-- empty result set is wrong, a single row holding NULL is right. Putting the
-- query in the SELECT list as a scalar subquery guarantees exactly one output row,
-- and the subquery itself yields NULL once DISTINCT + ORDER BY + OFFSET runs off
-- the end of the table.
--
-- DISTINCT is what makes this the second highest *salary* rather than the second
-- row: with salaries [300, 300, 200] the answer is 200, not 300.
--
-- `salary IS NOT NULL` is not needed for the judge's data (salaries are ints) but
-- makes the intent explicit, because PostgreSQL sorts NULLs first under DESC while
-- SQLite sorts them last -- without the guard the two engines would disagree on
-- NULL-bearing rows.
--
-- Time: O(n log n)   Space: O(n)   (n = number of Employee rows)

SELECT (
    SELECT DISTINCT salary
    FROM Employee
    WHERE salary IS NOT NULL
    ORDER BY salary DESC
    LIMIT 1 OFFSET 1
) AS "SecondHighestSalary";
