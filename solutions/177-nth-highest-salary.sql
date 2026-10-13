-- 177. Nth Highest Salary
-- https://leetcode.com/problems/nth-highest-salary/
--
-- This problem is judged as a stored function, not as a query: its test data
-- carries an `argument` (n) and the judge calls SELECT NthHighestSalary(n). A
-- bare SELECT cannot receive n, so the submission has to define the function --
-- it is still ONE statement, which is what the judge executes.
--
-- The function name is NthHighestSalary, NOT getNthHighestSalary. The expected
-- output labels its column "getNthHighestSalary(2)", but that is a column label,
-- not the identifier the harness invokes; naming the function after it produced
-- "function nthhighestsalary(integer) does not exist". PostgreSQL folds an
-- unquoted name to lower case, so the spelling here must match exactly.
--
-- The body ranks the distinct salaries with DENSE_RANK over the highest-first
-- order (over distinct values that is exactly "nth highest") and returns the one
-- whose rank is n. A SQL-language scalar function yields NULL when its query
-- produces no row, so n larger than the number of distinct salaries needs no
-- UNION, CASE or extra SELECT: the "fewer than n distinct salaries" rule falls
-- out of the empty result.
--
-- `salary IS NOT NULL` keeps NULL-bearing rows from being ranked, which matters
-- because PostgreSQL orders NULLs first under DESC while SQLite orders them last.
--
-- Time: O(n log n)   Space: O(n)   (n = number of Employee rows)

CREATE OR REPLACE FUNCTION NthHighestSalary(N INT) RETURNS INT AS $$
    SELECT salary
    FROM (
        SELECT salary,
               DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
        FROM (SELECT DISTINCT salary FROM Employee WHERE salary IS NOT NULL) AS distinct_salaries
    ) AS ranked
    WHERE rnk = N;
$$ LANGUAGE sql;
