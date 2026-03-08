# Median Employee Salary (LeetCode #569)

🔗 [LeetCode 569: Median Employee Salary](https://leetcode.com/problems/median-employee-salary/)

> **Difficulty:** Hard | **Interview Frequency:** Occasional

## Problem Statement

Find the median salary for each company. If a company has an even number of employees, return both middle salary values. The output should include `id`, `company` and `salary`.

## Thought Process

1. **What is the median?** The middle value in a sorted list. For odd count n, position (n+1)/2. For even count n, positions n/2 and n/2+1.
2. **How to find positional info in SQL?** ROW_NUMBER gives each row a position within its company partition. COUNT gives the total per company.
3. **How to select the middle position(s)?** FLOOR((cnt+1)/2) and CEIL((cnt+1)/2) produce the same value for odd counts (one row) and the two middle positions for even counts (two rows).

## Worked Example

Consider company A with 5 employees sorted by salary: [15, 341, 451, 513, 2341]. The count is 5 (odd), so the median is at position (5+1)/2 = 3. The FLOOR and CEIL of 3 are both 3, so we get one row: salary 451.

Now consider company B with 4 employees: [100, 200, 300, 400]. The count is 4 (even). FLOOR((4+1)/2) = 2, CEIL((4+1)/2) = 3. We return positions 2 and 3: salaries 200 and 300.

```
Company A (5 employees):
  rn | salary | cnt | FLOOR((6)/2) | CEIL((6)/2)
   1 |     15 |   5 |            3 |           3
   2 |    341 |   5 |            3 |           3
   3 |    451 |   5 |            3 |           3  <-- median
   4 |    513 |   5 |            3 |           3
   5 |   2341 |   5 |            3 |           3

WHERE rn BETWEEN 3 AND 3 -> row 3 (salary 451)

Company B (4 employees):
  rn | salary | cnt | FLOOR((5)/2) | CEIL((5)/2)
   1 |    100 |   4 |            2 |           3
   2 |    200 |   4 |            2 |           3  <-- median
   3 |    300 |   4 |            2 |           3  <-- median
   4 |    400 |   4 |            2 |           3

WHERE rn BETWEEN 2 AND 3 -> rows 2, 3 (salaries 200, 300)
```

## Approaches

### Approach 1: ROW_NUMBER + COUNT Window Functions

<details>
<summary>Explanation</summary>

Use ROW_NUMBER partitioned by company to assign positions, and COUNT to get the total per company. Then filter using the FLOOR/CEIL formula to identify the middle position(s).

The ORDER BY in ROW_NUMBER uses `salary, id` to break ties deterministically. Without the id tiebreaker, tied salaries would get arbitrary row numbers that could vary between runs.

This is O(n log n) for the sort within each partition, then O(n) for the scan.

</details>

### Approach 2: Recursive Trim (Academic)

<details>
<summary>Explanation</summary>

Repeatedly remove the minimum and maximum salary from each company until 1 or 2 rows remain. Those are the median(s).

```sql
WITH RECURSIVE trimmed AS (
    SELECT * FROM Employee_Company
    UNION ALL
    SELECT t.*
    FROM trimmed t
    JOIN (SELECT company, MIN(salary) AS mn, MAX(salary) AS mx
          FROM trimmed GROUP BY company HAVING COUNT(*) > 2) bounds
    ON t.company = bounds.company
    WHERE t.salary > bounds.mn AND t.salary < bounds.mx
)
-- Final iteration has 1-2 rows per company
```

This is elegant but impractical. Each recursion level removes 2 rows per company, so depth is O(n/2). Each level scans all remaining rows. Total work is O(n^2). The window function approach is strictly better for this problem.

</details>

## Edge Cases

| Scenario | Expected | Why |
|---|---|---|
| Odd count per company | Single median row | FLOOR = CEIL for odd (n+1)/2 |
| Even count per company | Two middle rows | FLOOR < CEIL gives two positions |
| Single employee | That employee | Position 1, FLOOR(1) = CEIL(1) = 1 |
| Tied salaries | Correct positional median | ORDER BY salary, id breaks ties |

## Interview Tips

> "I will use ROW_NUMBER and COUNT as window functions partitioned by company. ROW_NUMBER gives each employee a position in the salary ordering, and COUNT gives me the total. The FLOOR/CEIL trick on (count+1)/2 elegantly handles both odd and even cases in one WHERE clause."

**What the interviewer evaluates:** This tests whether you can use window functions for positional logic. The FLOOR/CEIL formula for median is a good pattern to know. Mentioning PERCENTILE_CONT as the production alternative shows pragmatism. If asked about the recursive approach, explaining why it is O(n^2) and impractical demonstrates algorithmic awareness.

## At Scale

The window function approach is O(n log n) for the sort within each company partition. For 10M employees across 100 companies, the sort is the bottleneck but completes in seconds on modern engines. The recursive trim approach is O(n^2), turning seconds into hours.

In production, use PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary) for median calculations. It is supported in BigQuery, Snowflake, DuckDB and Postgres. It handles odd/even cases automatically and is optimized internally (often using approximate algorithms for large datasets).

For approximate medians on very large datasets, engines like BigQuery offer APPROX_QUANTILES which trades precision for speed using HyperLogLog-style sketches.

## DE Application

Median computation appears in data profiling (median latency per endpoint), quality checks (median order value per segment) and reporting (median salary per department). The FLOOR/CEIL positional approach generalizes to any quantile: replace 0.5 with 0.95 for the 95th percentile.

Frequency-weighted medians (see problem 571) are common when data is pre-aggregated. PERCENTILE_CONT is the production solution for both raw and weighted medians.

## Related Problems

- [571. Find Median Given Frequency of Numbers](571_median_given_frequency.md) - Median with frequency table
- [178. Rank Scores](../../../sql/01_window_functions/problems/178_rank_scores.md) - DENSE_RANK basics
