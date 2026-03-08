# Rank Scores (LeetCode #178)

🔗 [LeetCode 178: Rank Scores](https://leetcode.com/problems/rank-scores/)

> **Difficulty:** Medium | **Interview Frequency:** Very Common

## Problem Statement

Write a SQL query to rank scores. The ranking should be dense (no gaps between consecutive rank numbers). If two scores are the same, they share the same rank. Return the result ordered by score descending with columns: score, rank.

## Thought Process

1. **Direct window function application:** DENSE_RANK() OVER (ORDER BY score DESC) is exactly what the problem asks for.
2. **Why DENSE_RANK not RANK:** DENSE_RANK produces no gaps: 1, 1, 2. RANK would produce 1, 1, 3 (skipping rank 2 after a tie). The problem explicitly requires dense ranking.
3. **Reserved word:** "rank" is a reserved keyword in most SQL dialects. Quote it as `"rank"` to use it as a column alias.

## Worked Example

DENSE_RANK assigns the same rank to equal values and increments by one for the next distinct value. There are no gaps in the sequence. This is in contrast to RANK, which leaves gaps proportional to the number of ties.

```
Scores table:
  id | score
  1  | 3.50
  2  | 3.65
  3  | 4.00
  4  | 3.85
  5  | 4.00
  6  | 3.65

DENSE_RANK() OVER (ORDER BY score DESC):
  score=4.00 -> rank 1 (ids 3, 5)
  score=3.85 -> rank 2 (id 4)
  score=3.65 -> rank 3 (ids 2, 6)
  score=3.50 -> rank 4 (id 1)

Compare with RANK():
  score=4.00 -> rank 1 (ids 3, 5)
  score=3.85 -> rank 3 (skipped 2)
  score=3.65 -> rank 4 (ids 2, 6)
  score=3.50 -> rank 6 (skipped 5)
```

## Approaches

### Approach 1: DENSE_RANK Window Function

<details>
<summary>Explanation</summary>

Apply DENSE_RANK with ORDER BY score DESC and alias the result as "rank" (quoted because it is a reserved word).

This is the simplest window function problem. The solution is a single SELECT with one window function. No subquery, no CTE, no join.

**Dialect notes:**
- DuckDB, Postgres, Snowflake: use double quotes `"rank"` for the alias
- MySQL: use backticks `` `rank` ``
- All major engines support DENSE_RANK

</details>

## Edge Cases

| Scenario | Expected | Why |
|---|---|---|
| Single score | Rank 1 | Only one value |
| All same score | All rank 1 | No distinct values to differentiate |
| All distinct | Ranks 1, 2, 3, ... | No ties |
| Two-way tie at top | Both rank 1, next is rank 2 | Dense ranking, no gaps |

## Interview Tips

> "DENSE_RANK over score descending gives exactly the ranking the problem asks for. I'll quote the alias 'rank' since it's a reserved keyword in most SQL dialects."

**What the interviewer evaluates:** This is a warm-up problem. Clean execution is expected quickly. The reserved word handling tests SQL syntax awareness. If a candidate hesitates on the difference between RANK and DENSE_RANK, it signals weak window function fundamentals.

## At Scale

DENSE_RANK requires a full sort of the score column: O(n log n). For 1B rows, this is a multi-minute sort without an index. Pre-materialized rank columns avoid re-sorting: add a `score_rank` column updated on INSERT/UPDATE via a trigger or batch job. In analytics warehouses, sorting is parallelized across nodes, so ranking 1B rows in Snowflake or BigQuery takes seconds, not minutes.

## DE Application

Dense ranking appears in leaderboard queries, percentile calculations and tiered pricing models. In data quality, ranking by frequency helps identify the most common values or outliers. Ranking with PARTITION BY (see LC 184/185) extends this to per-group leaderboards, which is a staple of product analytics dashboards.

## Related Problems

- [176. Second Highest Salary](176_second_highest_salary.md) - DENSE_RANK + filter
- [177. Nth Highest Salary](177_nth_highest_salary.md) - Parameterized rank filter
- [185. Department Top Three Salaries](185_department_top_three_salaries.md) - Partitioned ranking
