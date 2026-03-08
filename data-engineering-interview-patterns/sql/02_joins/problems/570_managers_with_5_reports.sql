/*
LeetCode 570: Managers with at Least 5 Direct Reports

Find managers who have at least 5 employees reporting directly to them.

Pattern: Self-join with GROUP BY + HAVING
*/

SELECT m.name
FROM Employee e
JOIN Employee m ON e.managerId = m.id
GROUP BY m.id, m.name
HAVING COUNT(*) >= 5;
