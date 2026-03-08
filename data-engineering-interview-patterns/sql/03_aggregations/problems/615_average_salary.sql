/*
LeetCode 615: Average Salary: Departments vs Company

For each month and department, determine if the department's average salary
is higher, lower, or equal to the company's average salary for that month.

Pattern: Two-level aggregation (department + company) with CTE and CASE comparison
*/

WITH monthly_dept AS (
    SELECT e.departmentId,
           DATE_TRUNC('month', s.pay_date) AS pay_month,
           AVG(s.amount) AS dept_avg
    FROM Salary s
    JOIN Employee e ON s.employee_id = e.id
    GROUP BY e.departmentId, DATE_TRUNC('month', s.pay_date)
),
monthly_company AS (
    SELECT DATE_TRUNC('month', pay_date) AS pay_month,
           AVG(amount) AS company_avg
    FROM Salary
    GROUP BY DATE_TRUNC('month', pay_date)
)
SELECT d.pay_month,
       d.departmentId AS department_id,
       CASE
           WHEN d.dept_avg > c.company_avg THEN 'higher'
           WHEN d.dept_avg < c.company_avg THEN 'lower'
           ELSE 'same'
       END AS comparison
FROM monthly_dept d
JOIN monthly_company c ON d.pay_month = c.pay_month
ORDER BY d.pay_month, d.departmentId;
