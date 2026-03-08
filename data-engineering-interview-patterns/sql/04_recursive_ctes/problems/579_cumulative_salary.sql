/*
LeetCode 579: Find Cumulative Salary of an Employee

For each employee, find the cumulative sum of their salary over
the previous 3 months (current + 2 prior). Exclude the most recent month
per employee.

Pattern: Window function with frame specification (ROWS BETWEEN)
*/

WITH ranked AS (
    SELECT id,
           month,
           salary,
           SUM(salary) OVER (
               PARTITION BY id
               ORDER BY month
               ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
           ) AS cumulative_salary,
           ROW_NUMBER() OVER (
               PARTITION BY id
               ORDER BY month DESC
           ) AS rn
    FROM Employee_Monthly
)
SELECT id, month, cumulative_salary AS Salary
FROM ranked
WHERE rn > 1
ORDER BY id, month DESC;
