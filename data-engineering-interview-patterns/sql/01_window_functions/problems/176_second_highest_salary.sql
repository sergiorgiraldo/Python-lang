/*
LeetCode 176: Second Highest Salary

Return the second highest DISTINCT salary from Employee.
If there is no second highest salary, return NULL.

Pattern: Window function (DENSE_RANK) or subquery with LIMIT/OFFSET
*/

-- Approach 1: DENSE_RANK window function
SELECT MAX(salary) AS SecondHighestSalary
FROM (
    SELECT salary,
           DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
    FROM Employee
) ranked
WHERE rnk = 2;
