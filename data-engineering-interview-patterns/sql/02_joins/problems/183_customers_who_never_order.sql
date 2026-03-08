/*
LeetCode 183: Customers Who Never Order

Find customers who never placed an order.

Pattern: LEFT JOIN + IS NULL (anti-join)
*/

SELECT c.name AS Customers
FROM Customers c
LEFT JOIN Orders o ON c.id = o.customerId
WHERE o.id IS NULL;
