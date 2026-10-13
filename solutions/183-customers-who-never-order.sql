-- 183. Customers Who Never Order
-- https://leetcode.com/problems/customers-who-never-order/
--
-- LEFT JOIN keeps every customer whether or not an order matches, so a customer
-- with no order survives the join carrying NULLs on the Orders side and is
-- exactly the row caught by "orders.id IS NULL". Orders.id is a primary key, so
-- it is never NULL in a genuine order: a NULL there can only mean the join found
-- no partner.
--
-- The alternative "customer.id NOT IN (SELECT customerId FROM Orders)" is not
-- used because it is not equivalent. If the subquery returns even one NULL
-- customerId, "NOT IN" is unknown for every customer and the query silently
-- returns nothing at all. A test asserts that trap directly.
--
-- Time: O(n + m) with a hash join, O(n log n) if the engine sorts. Space: O(n + m).
SELECT customer.name AS "Customers"
FROM Customers AS customer
LEFT JOIN Orders AS orders ON orders.customerId = customer.id
WHERE orders.id IS NULL;
