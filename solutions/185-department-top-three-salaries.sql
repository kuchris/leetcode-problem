-- 185. Department Top Three Salaries
-- https://leetcode.com/problems/department-top-three-salaries/
--
-- "Top three" counts distinct salaries, not employees. DENSE_RANK is therefore
-- the right window and RANK is not: two employees on the same salary share one
-- dense rank, so a department can report more than three rows while still naming
-- only three distinct salary levels. RANK would leave a gap after a tie and
-- could drop an employee who genuinely sits within the top three salaries.
--
-- Keeping rk <= 3 also covers small departments: with one or two distinct
-- salaries everyone ranks at or below 3, so they all appear. The inner join drops
-- departments with no employees, and employees whose departmentId matches no
-- department, because neither can be reported with a department name.
--
-- Time: O(n log n) to sort each partition inside the window, O(n) to scan. Space: O(n).
SELECT department.name AS "Department",
       ranked.name AS "Employee",
       ranked.salary AS "Salary"
FROM (
    SELECT name,
           salary,
           departmentId,
           DENSE_RANK() OVER (PARTITION BY departmentId ORDER BY salary DESC) AS rk
    FROM Employee
) AS ranked
INNER JOIN Department AS department ON department.id = ranked.departmentId
WHERE ranked.rk <= 3;
