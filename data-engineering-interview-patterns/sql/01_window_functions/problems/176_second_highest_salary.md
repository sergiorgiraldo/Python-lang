# Second Highest Salary (LeetCode #176)

🔗 [LeetCode 176: Second Highest Salary](https://leetcode.com/problems/second-highest-salary/)

> **Difficulty:** Medium | **Interview Frequency:** Very Common

## Problem Statement

Write a SQL query to find the second highest distinct salary from the Employee table. If there is no second highest salary, return NULL.

## Thought Process

1. **Why not just ORDER BY + LIMIT?** `ORDER BY salary DESC LIMIT 1 OFFSET 1` almost works, but returns no rows (instead of NULL) when there's no second salary. We need the result to be NULL, not an empty result set.
2. **Two approaches:** Use DENSE_RANK to rank salaries and filter for rank 2, or wrap the OFFSET query in a subquery (which returns NULL when the subquery is empty).
3. **DENSE_RANK vs RANK vs ROW_NUMBER:** DENSE_RANK handles ties correctly - two employees with the same highest salary both get rank 1, and the next distinct salary gets rank 2.

## Worked Example

The key decision is handling ties and the NULL case. DENSE_RANK assigns the same rank to tied values and leaves no gaps. If everyone has the same salary, there's only rank 1, so filtering for rank 2 returns nothing. Wrapping in MAX() converts the empty result to NULL.

```
Employee table:
  id | name  | salary
  1  | Alice | 300
  2  | Bob   | 300
  3  | Carol | 200
  4  | Dave  | 100

DENSE_RANK() OVER (ORDER BY salary DESC):
  salary=300 -> rank 1 (both Alice and Bob)
  salary=200 -> rank 2 (Carol)
  salary=100 -> rank 3 (Dave)

Filter WHERE rnk = 2 -> salary 200
MAX(salary) WHERE rnk = 2 -> 200

Edge case - all same salary:
  salary=100 -> rank 1 (everyone)
  Filter WHERE rnk = 2 -> empty
  MAX(salary) WHERE rnk = 2 -> NULL
```

## Approaches

### Approach 1: DENSE_RANK Window Function

<details>
<summary>Explanation</summary>

Rank all salaries with DENSE_RANK (no gaps for ties). Filter for rank 2. Wrap in MAX() to return NULL instead of empty result when rank 2 doesn't exist.

DENSE_RANK is the right choice because:
- ROW_NUMBER would assign different ranks to tied salaries (arbitrary tiebreak)
- RANK would skip rank 2 if two employees tie for rank 1 (ranks would be 1, 1, 3)
- DENSE_RANK assigns 1, 1, 2 for ties, which is what we want

**Dialect notes:**
- In BigQuery/Snowflake/DuckDB: use QUALIFY to filter without a subquery: `QUALIFY DENSE_RANK() OVER (ORDER BY salary DESC) = 2`
- In Postgres/MySQL: must use a subquery or CTE

</details>

### Approach 2: DISTINCT + OFFSET in Subquery

<details>
<summary>Explanation</summary>

Get distinct salaries sorted descending, skip 1, take 1. Wrap in a subquery so that when OFFSET returns no rows, the outer query returns NULL.

This is simpler to write but less extensible. For "Nth highest salary" (LC 177), the DENSE_RANK approach generalizes by changing the filter to `rnk = N`. The OFFSET approach changes `OFFSET N-1`.

</details>

## Edge Cases

| Scenario | Expected | Why |
|---|---|---|
| One employee | NULL | No second salary exists |
| All same salary | NULL | Only one distinct salary |
| Two employees, different salaries | Lower salary | Standard case |
| Negative salaries | Correct second highest | Negative numbers sort correctly |

## Interview Tips

> "I'll use DENSE_RANK to rank distinct salaries. DENSE_RANK handles ties correctly - if two people tie for first, the next distinct salary is rank 2, not rank 3. I'll wrap in MAX() to return NULL when there's no second salary."

**What the interviewer evaluates:** Understanding the difference between ROW_NUMBER, RANK and DENSE_RANK is fundamental for SQL interviews. This problem tests that directly. Being able to explain when each is appropriate (and why DENSE_RANK is correct here) shows SQL fluency.

## At Scale

DENSE_RANK requires a full sort of the salary column: O(n log n). For 1B employee records, this takes minutes without an index. With an index on salary, the database can read the top 2 distinct values directly: O(1). In production, "find the Nth value" queries use indexed columns. The OFFSET approach with an index is O(N) - fast for small N, impractical for large N. For analytics queries over large tables (daily active users ranked by engagement), pre-aggregating and caching rank results avoids repeated full-table sorts.

## DE Application

Finding the Nth highest/lowest value is common in data profiling: "what's the 95th percentile salary?" is `DENSE_RANK at position 0.05 * COUNT(*)`. Deduplication with ROW_NUMBER (a closely related window function) is one of the most common DE operations: `ROW_NUMBER() OVER (PARTITION BY key ORDER BY updated_at DESC)` with a filter for row 1 keeps the latest version of each record.

## Related Problems

- [177. Nth Highest Salary](177_nth_highest_salary.md) - Generalization
- [178. Rank Scores](178_rank_scores.md) - Direct DENSE_RANK application
- [185. Department Top Three Salaries](185_dept_top_three.md) - Partitioned ranking
