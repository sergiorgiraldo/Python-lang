/*
LeetCode 185: Department Top Three Salaries

Find employees whose salary is in the top 3 distinct salaries
for their department.

Pattern: DENSE_RANK with PARTITION BY + filter
*/

SELECT d.name AS Department,
       e.name AS Employee,
       e.salary AS Salary
FROM (
    SELECT *,
           DENSE_RANK() OVER (PARTITION BY departmentId ORDER BY salary DESC) AS rnk
    FROM Employee
) e
JOIN Department d ON e.departmentId = d.id
WHERE e.rnk <= 3;
