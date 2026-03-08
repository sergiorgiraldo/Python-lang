/*
Anti-join using NOT EXISTS (often more readable and sometimes faster).
*/

SELECT name AS Customers
FROM Customers c
WHERE NOT EXISTS (
    SELECT 1 FROM Orders o WHERE o.customerId = c.id
);
