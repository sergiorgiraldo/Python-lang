# Find Cumulative Salary of an Employee (LeetCode #579)

🔗 [LeetCode 579: Find Cumulative Salary of an Employee](https://leetcode.com/problems/find-cumulative-salary-of-an-employee/)

> **Difficulty:** Hard | **Interview Frequency:** Occasional

## Problem Statement

For each employee, compute the cumulative sum of their salary over the current month and the two months immediately before it (a 3-month rolling window). Exclude the most recent month for each employee. Order by id ascending and month descending.

## Thought Process

1. **Rolling sum of 3 months:** SUM with a ROWS BETWEEN 2 PRECEDING AND CURRENT ROW frame gives a 3-month rolling sum when ordered by month.
2. **Exclude the most recent month:** ROW_NUMBER ordered by month DESC marks the most recent month as rn=1. Filter WHERE rn > 1 removes it.
3. **Two window functions, one query:** Both SUM and ROW_NUMBER partition by id, so they share context. The SUM uses month ASC ordering (for the rolling window), while ROW_NUMBER uses month DESC (for identifying the most recent).

## Worked Example

Consider employee 1 with months [1, 2, 3, 4, 7]. The rolling sum builds up as we scan left to right, always summing the current row and up to 2 preceding rows. Month 7 is the most recent and gets excluded.

The ROWS frame counts physical rows, not month values. Even though there is a gap between months 4 and 7, the frame for month 7 still includes months 3, 4 and 7 (the three physical rows ending at month 7).

```
Employee 1, sorted by month ASC:
  month | salary | window contents           | cumulative | rn (DESC) | included?
      1 |     20 | [20]                       |         20 |         5 | yes
      2 |     30 | [20, 30]                   |         50 |         4 | yes
      3 |     40 | [20, 30, 40]               |         90 |         3 | yes
      4 |     60 | [30, 40, 60]               |        130 |         2 | yes
      7 |     90 | [40, 60, 90]               |        190 |         1 | NO (most recent)

Output for employee 1:
  id=1, month=4, Salary=130
  id=1, month=3, Salary=90
  id=1, month=2, Salary=50
  id=1, month=1, Salary=20
```

## Approaches

### Approach 1: SUM Window + ROW_NUMBER Exclusion

<details>
<summary>Explanation</summary>

Combine two window functions in a CTE:
- `SUM(salary) OVER (PARTITION BY id ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)` for the rolling sum
- `ROW_NUMBER() OVER (PARTITION BY id ORDER BY month DESC)` to identify the most recent month

Filter `WHERE rn > 1` to exclude the most recent month. Order by id ASC, month DESC.

This is O(n log n) for the sort, O(n) for the window scan.

</details>

## Edge Cases

| Scenario | Expected | Why |
|---|---|---|
| Single month per employee | Empty result | Only month is most recent, excluded |
| Two months | One row with its own salary | Second-to-last has no 2-preceding row, just itself |
| Three months | Two rows | Third (most recent) excluded; second gets 2-month sum |
| Gaps in months | ROWS still uses physical rows | Frame counts rows, not month distance |

## Interview Tips

> "I will use SUM with a ROWS BETWEEN 2 PRECEDING frame for the 3-month rolling sum, and ROW_NUMBER descending to identify and exclude the most recent month. The key subtlety is that ROWS counts physical rows, not logical month values."

**What the interviewer evaluates:** Combining two window functions (SUM with frame + ROW_NUMBER for exclusion) tests multi-step window function fluency. The ROWS vs RANGE distinction is a common follow-up question that tests depth. Candidates who proactively mention this distinction before being asked demonstrate mastery.

**Follow-up: ROWS vs RANGE.** If months have gaps, ROWS BETWEEN 2 PRECEDING counts the 2 preceding physical rows (which may span more than 2 calendar months). RANGE BETWEEN 2 PRECEDING AND CURRENT ROW would count by month distance (only months within 2 of the current). For gap-free months this doesn't matter. For gapped data, clarify the requirement with the interviewer.

## At Scale

Window functions with a fixed frame are streaming operations: O(n) time with O(frame_size) state per partition. For 1B salary records across 100K employees, the sort by (id, month) is the bottleneck. With data already partitioned by employee id and sorted by month (common in time-series tables), the window computation is a single-pass scan.

The exclusion pattern (compute the window, then filter) is cheap because ROW_NUMBER adds negligible overhead to the existing partition sort. The most recent month per employee is computed during the same pass.

## DE Application

Rolling sums and running totals with exclusions are everywhere in production:
- "Trailing 3-month revenue excluding the current incomplete month"
- "7-day moving average excluding today (incomplete data)"
- "Year-to-date totals refreshed daily, excluding the current month"

The pattern is always the same: compute the rolling aggregate, then use ROW_NUMBER or a date filter to exclude the incomplete period. In scheduling terms, a daily job computes the rolling sum for all periods, then the reporting layer filters to exclude the current (partial) period.

ROWS vs RANGE matters in practice when source data has gaps (missed ingestion days, weekends, holidays). Always clarify whether the business requirement is "previous N rows" or "previous N time units."

## Dialect Notes

Syntax is identical across all major engines. SUM() OVER with ROWS BETWEEN frame and self-exclusion via subquery are part of the SQL standard. The ROWS frame specification works the same in DuckDB, BigQuery, Snowflake, Spark SQL and Postgres.

## Related Problems

- [569. Median Employee Salary](569_median_employee_salary.md) - Positional window functions
