# Department Highest Salary (LeetCode #184)

🔗 [LeetCode 184: Department Highest Salary](https://leetcode.com/problems/department-highest-salary/)

> **Difficulty:** Medium | **Interview Frequency:** Very Common

## Problem Statement

Write a SQL query to find employees who have the highest salary in each department. If multiple employees share the highest salary in a department, return all of them.

## Thought Process

1. **PARTITION BY is the key concept:** We need the highest salary per department, not globally. PARTITION BY departmentId scopes the ranking to each department.
2. **RANK vs DENSE_RANK:** When filtering for rank 1, both produce the same result. Tied employees both get rank 1 regardless of which function we use. RANK is slightly more natural here ("the highest"), but DENSE_RANK works identically for the top position.
3. **Join back to Department:** The Employee table has departmentId but not the department name. Join to Department for the display name.

## Worked Example

PARTITION BY splits the data into groups before ranking. Within each partition, RANK assigns rank 1 to the highest salary. When multiple employees tie for the highest salary, they all get rank 1 and all appear in the result.

```
Employee table:                   Department table:
  id | name  | salary | deptId     id | name
  1  | Joe   | 85000  | 1          1  | IT
  2  | Henry | 80000  | 2          2  | Sales
  3  | Sam   | 60000  | 2
  4  | Max   | 90000  | 1

RANK() OVER (PARTITION BY departmentId ORDER BY salary DESC):
  IT partition:
    Max   90000 -> rank 1
    Joe   85000 -> rank 2
  Sales partition:
    Henry 80000 -> rank 1
    Sam   60000 -> rank 2

Filter WHERE rnk = 1:
  (IT, Max, 90000), (Sales, Henry, 80000)
```

## Approaches

### Approach 1: Window Function with PARTITION BY

<details>
<summary>Explanation</summary>

RANK (or DENSE_RANK) with PARTITION BY departmentId, ORDER BY salary DESC. Filter for rank 1. Join to Department for names.

This is one pass through Employee (plus the sort per partition) and one join. Clean, readable and the standard approach.

**Dialect notes:**
- BigQuery/Snowflake/DuckDB: use QUALIFY to avoid the subquery
- Postgres/MySQL: subquery or CTE required

</details>

### Approach 2: Correlated Subquery

<details>
<summary>Explanation</summary>

```sql
SELECT d.name AS Department, e.name AS Employee, e.salary AS Salary
FROM Employee e
JOIN Department d ON e.departmentId = d.id
WHERE e.salary = (
    SELECT MAX(salary) FROM Employee WHERE departmentId = e.departmentId
)
```

The correlated subquery runs once per row in the outer query. For large tables, this is significantly slower than the window function approach (O(n^2) without optimization, vs O(n log n) for the window function).

</details>

## Edge Cases

| Scenario | Expected | Why |
|---|---|---|
| Tie for highest | Both employees returned | RANK assigns 1 to both |
| Single employee in dept | That employee | Trivially rank 1 |
| Department with no employees | Not in result | JOIN excludes empty departments |
| Multiple departments | One winner per dept | PARTITION BY scopes the ranking |

## Interview Tips

> "I'll use RANK with PARTITION BY departmentId to find the highest salary per department. PARTITION BY is what makes this per-department rather than global. I'll filter for rank 1 and join to Department for the name."

**What the interviewer evaluates:** PARTITION BY is the most important window function concept. This tests it directly. Reaching for a correlated subquery instead of a window function is a yellow flag in a DE interview. It suggests the candidate is not comfortable with window functions and is falling back to older SQL patterns.

## At Scale

PARTITION BY departmentId is a local sort per department. If there are few departments (10-100), each partition is large but the sort is still efficient. If there are millions of "departments" (e.g., per-user aggregation), the sort overhead per partition adds up. At 1B employees across 100 departments, each partition has ~10M rows and sorts in seconds. Across 10M "departments" with ~100 rows each, the partition overhead dominates and hash aggregation (GROUP BY with MAX) may outperform the window function.

## DE Application

"Top performer per group" is a universal business query: highest revenue customer per region, most active user per cohort, best performing campaign per channel. In data pipelines, this pattern identifies the latest record per entity key (a variant of deduplication). The combination of PARTITION BY for grouping and ranking for selection is the backbone of analytical SQL.

## Related Problems

- [185. Department Top Three Salaries](185_department_top_three_salaries.md) - Extends to top N
- [176. Second Highest Salary](176_second_highest_salary.md) - Global ranking (no partition)
- [177. Nth Highest Salary](177_nth_highest_salary.md) - Parameterized rank filter
