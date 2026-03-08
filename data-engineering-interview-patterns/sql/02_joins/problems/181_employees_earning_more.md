# Employees Earning More Than Their Managers (LeetCode #181)

🔗 [LeetCode 181: Employees Earning More Than Their Managers](https://leetcode.com/problems/employees-earning-more-than-their-managers/)

> **Difficulty:** Easy | **Interview Frequency:** Common

## Problem Statement

Find the names of employees who earn more than their manager.

## Thought Process

1. **Self-join concept:** The Employee table plays two roles: employee and manager. We join it to itself, aliasing one copy as the employee (e) and the other as the manager (m).
2. **Join condition:** e.managerId = m.id links each employee to their manager's row.
3. **Filter:** WHERE e.salary > m.salary keeps only employees who out-earn their manager.
4. **NULL managers:** Employees with managerId = NULL have no manager. The INNER JOIN naturally excludes them because NULL never equals any id.

## Worked Example

The key insight is that a single table can represent a relationship between entities of the same type. The managerId column is a foreign key pointing back to the same table's id column. Joining the table to itself lets us compare each employee's salary directly to their manager's salary in a single row.

```
Employee table:
  id | name  | salary | managerId
  1  | Joe   | 70000  | 3
  2  | Henry | 80000  | 4
  3  | Sam   | 60000  | NULL
  4  | Max   | 90000  | NULL

Self-join: Employee e JOIN Employee m ON e.managerId = m.id

  e.name=Joe,   e.salary=70000, m.name=Sam, m.salary=60000  -> 70000 > 60000 = YES
  e.name=Henry, e.salary=80000, m.name=Max, m.salary=90000  -> 80000 > 90000 = NO

  Sam and Max have NULL managerId -> no match in join -> excluded

Result: Joe
```

## Approaches

### Approach 1: Self-Join

<details>
<summary>Explanation</summary>

Join Employee to itself. The left copy is the employee, the right copy is the manager. Filter for employees whose salary exceeds their manager's.

```sql
SELECT e.name AS Employee
FROM Employee e
JOIN Employee m ON e.managerId = m.id
WHERE e.salary > m.salary;
```

INNER JOIN is correct here because we only want employees who have a manager and earn more than that manager. Employees without managers (NULL managerId) are correctly excluded.

</details>

### Approach 2: Correlated Subquery

<details>
<summary>Explanation</summary>

For each employee, look up the manager's salary with a subquery.

```sql
SELECT name AS Employee
FROM Employee e
WHERE salary > (
    SELECT salary FROM Employee WHERE id = e.managerId
);
```

This is semantically equivalent. The subquery returns NULL when managerId is NULL, and the > comparison with NULL evaluates to false, so employees without managers are correctly excluded. The self-join is more readable and typically performs the same or better.

</details>

## Edge Cases

| Scenario | Expected | Why |
|---|---|---|
| Employee with no manager (NULL managerId) | Excluded | INNER JOIN filters NULLs |
| Equal salary | Excluded | Strictly greater, not >= |
| All employees earn less than managers | Empty result | No matches |
| Manager also has a manager | Both comparisons evaluated independently | Each row is an employee |

## Interview Tips

> "I'll use a self-join since the employee-manager relationship is within the same table. I alias one copy as the employee and one as the manager, join on managerId = id, and filter where the employee's salary exceeds the manager's."

**What the interviewer evaluates:** Self-join is a fundamental SQL concept. Not recognizing that you can join a table to itself is a knowledge gap that concerns interviewers. The interviewer also checks whether you understand how NULL managerId behaves with INNER JOIN (it gets filtered out naturally). Mentioning the correlated subquery alternative shows flexibility.

## At Scale

Self-join on an indexed id column is O(n). The hash join builds a hash table on the manager side (id, salary) and probes with the employee side (managerId). The hash table contains one entry per employee who is a manager, which is usually much smaller than the full table. For 10M employees with 50K managers, the hash table is 50K entries and the probe scans 10M rows.

Without an index, the optimizer still uses a hash join (O(n) expected). Nested loop join would be O(n^2) and is only chosen for very small tables or when an index makes it efficient.

## DE Application

Self-joins for hierarchical comparisons appear frequently in analytics:
- "Find stores outperforming their regional average" (store → region self-referencing)
- "Find months where revenue exceeded the previous year's same month" (time-series self-join)
- "Find pipeline stages that take longer than their parent stage" (DAG self-join)

The pattern generalizes to any comparison between related entities in the same table.

## Dialect Notes

Syntax is identical across all major engines. Self-joins, comparison operators and column aliasing are part of the SQL standard with no dialect variation.

## Related Problems

- [570. Managers with at Least 5 Reports](570_managers_with_5_reports.md) - Self-join + GROUP BY + HAVING
- [184. Department Highest Salary](../01_window_functions/problems/184_department_highest_salary.md) - Comparison within groups
