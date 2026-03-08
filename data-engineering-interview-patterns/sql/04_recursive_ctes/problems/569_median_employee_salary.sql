/*
LeetCode 569: Median Employee Salary

Find the median salary for each company. If even number of employees,
return both middle values.

Pattern: ROW_NUMBER + COUNT to identify middle positions
Note: This can be solved without recursive CTEs, but LeetCode categorizes
it here. We solve it with window functions (more practical) and note
the recursive alternative.
*/

WITH numbered AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY company ORDER BY salary, id) AS rn,
           COUNT(*) OVER (PARTITION BY company) AS cnt
    FROM Employee_Company
)
SELECT id, company, salary
FROM numbered
WHERE rn BETWEEN FLOOR((cnt + 1) / 2.0) AND CEIL((cnt + 1) / 2.0)
ORDER BY company, salary;
