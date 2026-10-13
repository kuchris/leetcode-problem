-- 196. Delete Duplicate Emails
-- https://leetcode.com/problems/delete-duplicate-emails/
--
-- This is a DELETE because the judge runs the statement and then displays the
-- Person table (the statement says so outright: "you are supposed to write a
-- DELETE statement and not a SELECT one"). A SELECT that returns the survivors
-- would leave the duplicates in the table.
--
-- MIN(id) GROUP BY email is the survivor set: one row per email, always the
-- smallest id, which is precisely "keeping only one unique email with the
-- smallest id". NOT IN removes every other row, i.e. exactly the duplicates.
--
-- id is the primary key, so the subquery can never return NULL and NOT IN cannot
-- degrade into "nothing matches". email is never NULL ("Each row of this table
-- contains an email"), so GROUP BY forms one group per email rather than lumping
-- the NULLs together.
--
-- Time: O(n log n) to group n rows   Space: O(d) for d distinct emails

DELETE FROM Person
WHERE id NOT IN (
    SELECT MIN(id)
    FROM Person
    GROUP BY email
);
