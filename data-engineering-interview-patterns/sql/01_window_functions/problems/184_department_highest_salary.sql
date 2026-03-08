/*
LeetCode 184: Department Highest Salary

Find employees who have the highest salary in each department.
Multiple employees can share the highest salary.

Pattern: Window function (RANK/DENSE_RANK) with PARTITION BY
*/

SELECT d.name AS Department,
       e.name AS Employee,
       e.salary AS Salary
FROM (
    SELECT *,
           RANK() OVER (PARTITION BY departmentId ORDER BY salary DESC) AS rnk
    FROM Employee
) e
JOIN Department d ON e.departmentId = d.id
WHERE e.rnk = 1;
