/*
LeetCode 177: Nth Highest Salary

Return the Nth highest DISTINCT salary. Return NULL if it doesn't exist.
This generalizes LC 176 to arbitrary N.

Pattern: DENSE_RANK window function with parameterized filter
Note: LeetCode uses a function wrapper. We parameterize with a CTE.
      Tests replace {n} with the actual value via string formatting.
*/

WITH ranked AS (
    SELECT DISTINCT salary,
           DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
    FROM Employee
)
SELECT MAX(salary) AS NthHighestSalary
FROM ranked
WHERE rnk = {n};
