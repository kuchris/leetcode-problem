-- 175. Combine Two Tables
-- https://leetcode.com/problems/combine-two-tables/
--
-- A LEFT JOIN keeps every row of Person and fills the Address columns with NULL
-- for the persons whose personId never appears in Address -- which is exactly the
-- "report null instead" rule. personId is the join key; addressId is not used.
--
-- Invariant: one result row per (Person row x matching Address row), so a person
-- with no address contributes exactly one row of NULLs and a person with two
-- addresses contributes two rows. The statement fixes no order ("return the
-- result table in any order"), so no ORDER BY is added. The aliases pin the
-- column names to the exact camel case the result table uses, because PostgreSQL
-- folds unquoted identifiers to lower case.
--
-- Time: O(|Person| * matches) with an index on Address(personId)   Space: O(rows)

SELECT p.firstName AS "firstName",
       p.lastName AS "lastName",
       a.city,
       a.state
FROM Person AS p
LEFT JOIN Address AS a
       ON a.personId = p.personId;
