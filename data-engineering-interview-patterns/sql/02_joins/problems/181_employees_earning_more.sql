/*
LeetCode 181: Employees Earning More Than Their Managers

Find employees who earn more than their manager.

Pattern: Self-join (joining a table to itself)
*/

SELECT e.name AS Employee
FROM Employee e
JOIN Employee m ON e.managerId = m.id
WHERE e.salary > m.salary;
