# Managers with at Least 5 Direct Reports (LeetCode #570)

🔗 [LeetCode 570: Managers with at Least 5 Direct Reports](https://leetcode.com/problems/managers-with-at-least-five-direct-reports/)

> **Difficulty:** Medium | **Interview Frequency:** Common

## Problem Statement

Find the names of managers who have at least 5 employees reporting directly to them.

## Thought Process

1. **Self-join:** Join Employee (as reports) to Employee (as managers) on managerId = id. This pairs each employee with their manager.
2. **COUNT per manager:** GROUP BY the manager's id and name, COUNT the reports.
3. **HAVING >= 5:** Filter groups after aggregation. WHERE cannot filter on aggregates.

## Worked Example

The approach combines a self-join (to pair employees with managers) with GROUP BY + HAVING (to count and filter). The INNER JOIN naturally excludes employees with NULL managerId, so only actual manager-report relationships are counted.

```
Employee table:
  id | name  | managerId
  1  | Boss  | NULL
  2  | A     | 1
  3  | B     | 1
  4  | C     | 1
  5  | D     | 1
  6  | E     | 1
  7  | F     | 1
  8  | Other | NULL

Self-join e.managerId = m.id:
  (A, Boss), (B, Boss), (C, Boss), (D, Boss), (E, Boss), (F, Boss)

GROUP BY m.id, m.name:
  Boss -> COUNT(*) = 6

HAVING COUNT(*) >= 5:
  Boss qualifies (6 >= 5)

Result: Boss
```

## Approaches

### Approach 1: Self-Join + GROUP BY + HAVING

<details>
<summary>Explanation</summary>

```sql
SELECT m.name
FROM Employee e
JOIN Employee m ON e.managerId = m.id
GROUP BY m.id, m.name
HAVING COUNT(*) >= 5;
```

The self-join produces one row per (employee, manager) pair. Grouping by manager and counting gives the number of direct reports. HAVING filters for the threshold.

</details>

### Approach 2: Subquery

<details>
<summary>Explanation</summary>

```sql
SELECT name
FROM Employee
WHERE id IN (
    SELECT managerId
    FROM Employee
    GROUP BY managerId
    HAVING COUNT(*) >= 5
);
```

The subquery finds manager ids with 5+ reports. The outer query retrieves their names. This avoids the self-join by separating the counting and name lookup into two steps.

</details>

## Edge Cases

| Scenario | Expected | Why |
|---|---|---|
| Manager with exactly 5 | Included | >= 5 |
| Manager with 4 | Excluded | < 5 |
| Employee with no reports | Excluded | Never appears as m in the join |
| No managers meet threshold | Empty result | HAVING filters all groups |
| NULL managerId | Excluded from count | INNER JOIN filters NULLs |

## Interview Tips

> "I'll self-join Employee to pair each report with their manager, then GROUP BY the manager and use HAVING COUNT(*) >= 5. HAVING filters after grouping, while WHERE filters before. The INNER JOIN naturally excludes employees without a manager."

**What the interviewer evaluates:** HAVING vs WHERE confusion is surprisingly common among candidates. This problem tests that distinction directly. WHERE filters individual rows before grouping. HAVING filters groups after aggregation. Using WHERE COUNT(*) >= 5 is a syntax error. The interviewer also checks whether you can combine self-join with aggregation, which builds on the simpler self-join from problem 181.

## At Scale

GROUP BY managerId is a hash aggregation. For 10M employees, the hash table has at most as many entries as there are distinct managers, which is usually orders of magnitude smaller than the total row count. A company with 10M employees might have 500K managers, so the hash table is 500K entries.

The self-join itself is O(n): build a hash table from the manager side (id) and probe with the employee side (managerId). Combined with the GROUP BY, the full operation is O(n) in time and O(m) in memory where m is the number of distinct managers.

In distributed engines, both the self-join and the GROUP BY can be partitioned by the same key (managerId/id), keeping the data co-located.

## DE Application

Finding entities exceeding a threshold in related data is a common pattern:
- "Products with 100+ reviews" (products JOIN reviews GROUP BY product HAVING COUNT >= 100)
- "Tables with 50+ downstream dependencies" (lineage graph aggregation)
- "API endpoints with 1000+ errors per hour" (error logs grouped by endpoint)
- "Users with 10+ sessions today" (session table aggregation)

The HAVING clause is the standard SQL mechanism for threshold-based filtering on aggregated data.

## Dialect Notes

Syntax is identical across all major engines. Self-joins, GROUP BY, HAVING and COUNT are part of the SQL standard with no dialect variation.

## Related Problems

- [181. Employees Earning More](181_employees_earning_more.md) - Basic self-join
- [262. Trips and Users](262_trips_and_users.md) - JOIN + aggregation
