# Nth Highest Salary (LeetCode #177)

🔗 [LeetCode 177: Nth Highest Salary](https://leetcode.com/problems/nth-highest-salary/)

> **Difficulty:** Medium | **Interview Frequency:** Common

## Problem Statement

Write a SQL query to find the Nth highest distinct salary from the Employee table. If there is no Nth highest salary, return NULL. This generalizes LC 176 from "second" to an arbitrary N.

## Thought Process

1. **Generalize LC 176:** The second highest salary is just N=2. The same DENSE_RANK approach works for any N by changing the filter value.
2. **DENSE_RANK is the natural fit:** Rank all distinct salaries, filter for rank N. DENSE_RANK produces no gaps (1, 1, 2 not 1, 1, 3), so rank N corresponds to the Nth distinct value.
3. **NULL handling:** When N exceeds the number of distinct salaries, the filter returns no rows. Wrapping in MAX() converts the empty result to NULL.
4. **Parameterization:** LeetCode uses a SQL function. In practice, we parameterize with a placeholder that the caller substitutes.

## Worked Example

Start with the same intuition as LC 176. DENSE_RANK assigns consecutive rank numbers to distinct salary values. Filtering for rank N picks the Nth highest. If there are fewer than N distinct salaries, the filter matches nothing, and MAX() over an empty set returns NULL.

```
Employee table:
  id | name  | salary
  1  | Alice | 300
  2  | Bob   | 300
  3  | Carol | 200
  4  | Dave  | 100

DENSE_RANK() OVER (ORDER BY salary DESC):
  salary=300 -> rank 1 (Alice and Bob)
  salary=200 -> rank 2 (Carol)
  salary=100 -> rank 3 (Dave)

N=1: MAX(salary) WHERE rnk = 1 -> 300
N=2: MAX(salary) WHERE rnk = 2 -> 200
N=3: MAX(salary) WHERE rnk = 3 -> 100
N=4: MAX(salary) WHERE rnk = 4 -> NULL (no rank 4)
```

## Approaches

### Approach 1: DENSE_RANK Window Function

<details>
<summary>Explanation</summary>

Rank distinct salaries with DENSE_RANK, filter for rank N. Wrap in MAX() to return NULL when rank N does not exist.

This is the direct generalization of LC 176. The only change is replacing the hardcoded `rnk = 2` with `rnk = N`.

DENSE_RANK is the right choice because:
- ROW_NUMBER would assign different ranks to tied salaries
- RANK would skip numbers after ties (1, 1, 3), so rank N might not mean the Nth distinct value
- DENSE_RANK assigns 1, 1, 2 for ties, which is what we want

**Dialect notes:**
- BigQuery/Snowflake/DuckDB support QUALIFY: `QUALIFY DENSE_RANK() OVER (ORDER BY salary DESC) = N`
- Postgres/MySQL require a subquery or CTE

</details>

### Approach 2: DISTINCT + OFFSET

<details>
<summary>Explanation</summary>

Get distinct salaries sorted descending, skip N-1, take 1. Wrap in a subquery for the NULL case.

```sql
SELECT (
    SELECT DISTINCT salary
    FROM Employee
    ORDER BY salary DESC
    LIMIT 1 OFFSET N-1
) AS NthHighestSalary;
```

Simpler to write for small N. Less flexible if you need multiple rank values in the same query.

</details>

## Edge Cases

| Scenario | Expected | Why |
|---|---|---|
| N=1 | Highest salary | Standard case |
| N exceeds distinct count | NULL | No Nth rank exists |
| Ties at rank N | That salary value | DENSE_RANK handles ties |
| Single employee, N=1 | That salary | Only one distinct value |
| Single employee, N=2 | NULL | No second distinct salary |

## Interview Tips

> "This generalizes the second highest salary problem. I'll use DENSE_RANK to assign consecutive ranks to distinct salaries and filter for rank N. If N exceeds the number of distinct salaries, MAX() over the empty result gives NULL."

**What the interviewer evaluates:** This tests whether you can generalize a solution. Starting from LC 176 and parameterizing it shows systematic thinking. Candidates who recognize DENSE_RANK immediately demonstrate they understand the ranking function family. Mention ROW_NUMBER vs RANK vs DENSE_RANK and when each applies.

## At Scale

For small N (top 10, top 100), an index on salary allows the database to scan only N distinct values: effectively O(N). For large N or analytics queries ("what is the salary at each percentile?"), the full sort is O(n log n) on the salary column. Pre-aggregating distinct salaries with their ranks into a materialized view avoids re-sorting on repeated queries across many N values. At 1B rows, the sort dominates; partitioning the table by a coarse key (department, region) limits sort scope.

## DE Application

The "Nth value" pattern appears in data profiling and data quality checks: "what is the 99th percentile latency?" is a ranking query. In pipeline orchestration, "find the 3rd most recent successful run" uses the same DENSE_RANK pattern. The parameterized approach also maps to dynamic dashboards where users select N from a dropdown.

## Related Problems

- [176. Second Highest Salary](176_second_highest_salary.md) - Special case (N=2)
- [178. Rank Scores](178_rank_scores.md) - Direct DENSE_RANK application
- [185. Department Top Three Salaries](185_department_top_three_salaries.md) - Top N per partition
