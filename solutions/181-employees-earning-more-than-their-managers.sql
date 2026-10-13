-- 181. Employees Earning More Than Their Managers
-- https://leetcode.com/problems/employees-earning-more-than-their-managers/
--
-- Self-join Employee to itself, pairing each employee with the row whose id is
-- that employee's managerId, and keep the pairs where the employee earns
-- strictly more. Ties do not qualify, which is why the comparison is ">".
--
-- The join is what decides the employees without a usable manager. An employee
-- whose managerId is NULL, or points at an id that is not in the table, matches
-- no row, so the pair never forms and the employee drops out. That is the
-- correct reading rather than a lost row: with no manager row there is no salary
-- to compare against, so "earns more than their manager" cannot be satisfied.
-- The official example agrees, since Sam and Max both carry a NULL managerId
-- and neither appears in its expected output.
--
-- Time: O(n log n) for the join and O(n) to scan the pairs. Space: O(n).
SELECT employee.name AS "Employee"
FROM Employee AS employee
INNER JOIN Employee AS manager ON manager.id = employee.managerId
WHERE employee.salary > manager.salary;
