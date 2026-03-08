/*
LeetCode 176: Second Highest Salary - Alternative approach

Uses DISTINCT + OFFSET instead of window function.
*/

SELECT (
    SELECT DISTINCT salary
    FROM Employee
    ORDER BY salary DESC
    LIMIT 1 OFFSET 1
) AS SecondHighestSalary;
