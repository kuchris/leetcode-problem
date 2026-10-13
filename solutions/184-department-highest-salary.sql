-- 184. Department Highest Salary
-- https://leetcode.com/problems/department-highest-salary/
--
-- DENSE_RANK numbers each department's employees from the top salary down, so
-- every employee tied on their department's maximum lands on rank 1 and all of
-- them are reported. RANK gives the same answer for "highest", since ties there
-- also share rank 1, but DENSE_RANK states the tie behaviour plainly and is the
-- same function 185 needs.
--
-- The join to Department is an inner join, which is the correct behaviour here:
-- a department with no employees has no highest salary to report, and an
-- employee whose departmentId matches no department cannot be labelled with a
-- department name.
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
WHERE ranked.rk = 1;
