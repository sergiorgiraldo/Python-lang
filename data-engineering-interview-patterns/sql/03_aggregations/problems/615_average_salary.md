# Average Salary: Departments vs Company (LeetCode #615)

🔗 [LeetCode 615: Average Salary: Departments vs Company](https://leetcode.com/problems/average-salary-departments-vs-company/)

> **Difficulty:** Hard | **Interview Frequency:** Occasional

## Problem Statement

For each month and department, determine whether the department's average salary is higher, lower or equal to the company's average salary for that month. Output the pay_month, department_id and comparison result ('higher', 'lower' or 'same').

## Thought Process

1. **Two levels of aggregation:** Department-level average and company-level average, both per month.
2. **CTEs for clarity:** One CTE computes monthly department averages. Another CTE computes monthly company averages.
3. **Join and compare:** Join the two CTEs on pay_month. Use CASE WHEN to classify each department as higher, lower or same.

## Worked Example

The query decomposes the problem into two aggregation levels using CTEs. The department CTE groups by (departmentId, month). The company CTE groups by month alone. Joining them on month and comparing with CASE produces the final classification.

```
Employee:                    Salary:
  id | departmentId           id | employee_id | amount | pay_date
  1  | 1                      1  | 1           | 9000   | 2017-03-31
  2  | 1                      2  | 2           | 6000   | 2017-03-31
  3  | 2                      3  | 3           | 3000   | 2017-03-31

monthly_dept CTE:
  departmentId=1, month=2017-03 -> AVG = (9000+6000)/2 = 7500
  departmentId=2, month=2017-03 -> AVG = 3000

monthly_company CTE:
  month=2017-03 -> AVG = (9000+6000+3000)/3 = 6000

JOIN + CASE:
  dept 1: 7500 > 6000 -> 'higher'
  dept 2: 3000 < 6000 -> 'lower'
```

## Approaches

### Approach 1: Two CTEs + JOIN + CASE

<details>
<summary>Explanation</summary>

```sql
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
```

Two CTEs separate the aggregation levels cleanly. The join combines them for comparison. This is the most readable approach for multi-level aggregation problems.

</details>

### Approach 2: Window Function for Company Average

<details>
<summary>Explanation</summary>

```sql
SELECT pay_month,
       departmentId AS department_id,
       CASE
           WHEN dept_avg > company_avg THEN 'higher'
           WHEN dept_avg < company_avg THEN 'lower'
           ELSE 'same'
       END AS comparison
FROM (
    SELECT DATE_TRUNC('month', s.pay_date) AS pay_month,
           e.departmentId,
           AVG(s.amount) AS dept_avg,
           AVG(AVG(s.amount)) OVER (PARTITION BY DATE_TRUNC('month', s.pay_date)) AS company_avg
    FROM Salary s
    JOIN Employee e ON s.employee_id = e.id
    GROUP BY e.departmentId, DATE_TRUNC('month', s.pay_date)
) t
ORDER BY pay_month, department_id;
```

AVG(AVG(amount)) OVER (PARTITION BY month) computes the company average as a window function over the department-level aggregation. This uses a single query block instead of two CTEs. The nested aggregate inside a window function (`AVG(AVG(amount)) OVER (...)`) is a valid but less readable pattern.

**Note:** The window-based company average here computes the average of department averages, not the average of individual salaries. These differ when departments have different sizes. For the correct company average weighted by employee count, the two-CTE approach is more precise.

</details>

## Edge Cases

| Scenario | Expected | Why |
|---|---|---|
| Single department | Always 'same' | Dept average equals company average |
| All employees same salary | All 'same' | Every average is identical |
| Multiple months | Independent comparisons per month | Each month is computed separately |
| Department with one employee | Compared to full company | That employee's salary is the dept average |

## Interview Tips

> "I'll decompose this into two aggregation levels using CTEs: one for monthly department averages and one for monthly company averages. Then I'll join them on month and use CASE to classify as higher, lower or same. The CTE structure makes each level of aggregation explicit and testable."

**What the interviewer evaluates:** Multi-level aggregation with comparison tests SQL fluency. The CTE structure (department CTE + company CTE + join + CASE) shows clear problem decomposition. The interviewer may ask "what if you need percentiles instead of averages?" which requires window functions or APPROX_QUANTILE. They may also ask about the difference between average-of-averages and weighted average, which tests statistical awareness.

## At Scale

Two GROUP BY operations plus a join. For large payroll data (100M salary records), the GROUP BY operations are the bottleneck. The department-level aggregation produces O(departments * months) rows. The company-level produces O(months) rows. Both are small relative to the input.

Pre-aggregated monthly summaries (materialized views or summary tables) avoid recomputation. In production, salary data is often pre-aggregated into monthly/quarterly summaries during ETL, making this query trivial at query time.

In distributed engines, the join between department-level and company-level results is a broadcast join since the company-level result has one row per month.

## DE Application

Comparing segment performance to overall benchmarks is a standard analytics pattern:

- "Is this region above or below the company average revenue?"
- "Is this pipeline slower than the platform average?"
- "Does this customer segment have higher churn than the overall rate?"
- "Is this warehouse's query latency above the fleet median?"

The two-CTE structure (segment aggregation + overall aggregation + join + compare) is the general template for benchmark comparisons.

## Dialect Notes

Date truncation syntax varies:

- **DuckDB / Postgres**: `DATE_TRUNC('month', pay_date)`
- **BigQuery**: `DATE_TRUNC(pay_date, MONTH)` (argument order reversed)
- **Snowflake**: `DATE_TRUNC('month', pay_date)` (same as Postgres)
- **Spark SQL**: `date_trunc('month', pay_date)` (lowercase function name)
- **MySQL**: `DATE_FORMAT(pay_date, '%Y-%m')` (no DATE_TRUNC; use FORMAT instead)

The nested aggregate inside a window function (`AVG(AVG(amount)) OVER (...)`) is supported in all major engines. The CASE-based comparison logic is universal.

## Related Problems

- [511. Game Play Analysis I](511_game_play_analysis_i.md) - Simple GROUP BY + MIN
- [574. Winning Candidate](574_winning_candidate.md) - JOIN + GROUP BY
- [585. Investments in 2016](585_investments_in_2016.md) - Filtering on aggregate conditions
