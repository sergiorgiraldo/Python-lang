# Department Top Three Salaries (LeetCode #185)

🔗 [LeetCode 185: Department Top Three Salaries](https://leetcode.com/problems/department-top-three-salaries/)

> **Difficulty:** Hard | **Interview Frequency:** Common

## Problem Statement

Write a SQL query to find employees whose salary is in the top 3 distinct salaries for their department. A department with fewer than 3 distinct salaries should include all employees.

## Thought Process

1. **DENSE_RANK, not RANK:** We want the top 3 distinct salary values. DENSE_RANK assigns consecutive ranks to distinct values (1, 1, 2, 3). RANK would skip ranks after ties (1, 1, 3), potentially excluding valid employees.
2. **PARTITION BY + filter:** DENSE_RANK with PARTITION BY departmentId scopes the ranking per department. Filter for `rnk <= 3` includes everyone in the top 3 distinct salary tiers.
3. **Ties expand the result:** If 5 people tie for the 3rd highest salary, all 5 are included. The result can have more than 3 rows per department.

## Worked Example

DENSE_RANK assigns ranks without gaps. Within each department, the top 3 distinct salary values get ranks 1, 2 and 3. Every employee at those salary levels is included, regardless of how many employees share a salary.

```
IT Department:
  name   | salary | DENSE_RANK
  Max    | 90000  | 1
  Joe    | 85000  | 2
  Randy  | 85000  | 2
  Will   | 70000  | 3
  Janet  | 69000  | 4   <- excluded (rank > 3)

Top 3 distinct salaries: 90000, 85000, 70000
Employees included: Max, Joe, Randy, Will (4 employees, 3 salary tiers)
Janet excluded: 69000 is the 4th distinct salary
```

## Approaches

### Approach 1: DENSE_RANK with PARTITION BY

<details>
<summary>Explanation</summary>

DENSE_RANK over each department, filter for rank <= 3. Join to Department for names.

This is a single sort pass per partition plus one join. The query is nearly identical to LC 184, with the filter changed from `= 1` to `<= 3` and DENSE_RANK replacing RANK.

**Dialect notes:**
- BigQuery/Snowflake/DuckDB: `QUALIFY DENSE_RANK() OVER (...) <= 3`
- Postgres/MySQL: subquery or CTE required

</details>

### Approach 2: Correlated Subquery

<details>
<summary>Explanation</summary>

Count how many distinct salaries are higher than the current employee's salary within the same department. If fewer than 3 are higher, the employee is in the top 3.

```sql
WHERE (SELECT COUNT(DISTINCT e2.salary) FROM Employee e2
       WHERE e2.departmentId = e1.departmentId AND e2.salary > e1.salary) < 3
```

This is O(n^2) and significantly harder to read. It exists as a pre-window-function technique.

</details>

## Edge Cases

| Scenario | Expected | Why |
|---|---|---|
| Fewer than 3 distinct salaries | All employees | Everyone is in "top 3" |
| Ties at rank 3 | All tied employees included | DENSE_RANK gives them all rank 3 |
| Many employees, many ties | Can exceed 3 rows per dept | Ranking is by salary tier, not headcount |
| Empty department | Not in result | JOIN excludes it |

## Interview Tips

> "DENSE_RANK is critical here because we want top 3 distinct salaries, not top 3 rows. If two people tie for first, the next salary is rank 2, not rank 3. I'll partition by department and filter for rank <= 3."

**What the interviewer evaluates:** If you know DENSE_RANK + PARTITION BY, this is a 2-minute problem. If you do not, it is extremely hard. This is why window functions are the single most important SQL topic for DE interviews. The choice of DENSE_RANK over RANK shows understanding of the difference. The ability to articulate why ties expand the result set shows depth.

## At Scale

DENSE_RANK over partitions is one sort pass per partition. For 1B rows across 100 departments, each partition sorts ~10M rows: fast on modern hardware. The correlated subquery alternative is O(n^2): for 10M rows per department, each row triggers a subquery scanning up to 10M rows. The window function is orders of magnitude faster at scale.

## DE Application

"Top N per group" is one of the most common analytics patterns. Top N customers by revenue per region. Top N products by sales per category. Top N pages by traffic per day. In data pipelines, this pattern feeds dashboards, reports and alerts. DENSE_RANK + PARTITION BY is the universal tool for these queries.

## Related Problems

- [184. Department Highest Salary](184_department_highest_salary.md) - Special case (top 1)
- [177. Nth Highest Salary](177_nth_highest_salary.md) - Global Nth (no partition)
- [178. Rank Scores](178_rank_scores.md) - Dense ranking basics
