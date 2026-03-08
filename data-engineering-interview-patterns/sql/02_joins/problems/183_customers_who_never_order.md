# Customers Who Never Order (LeetCode #183)

🔗 [LeetCode 183: Customers Who Never Order](https://leetcode.com/problems/customers-who-never-order/)

> **Difficulty:** Easy | **Interview Frequency:** Very Common

## Problem Statement

Find the names of customers who never placed an order.

## Thought Process

1. **Anti-join pattern:** We need customers that do NOT exist in the Orders table. This is the opposite of a regular join.
2. **Three syntaxes:** LEFT JOIN + WHERE IS NULL, NOT EXISTS, NOT IN. All express anti-join but with different trade-offs.
3. **NULL trap with NOT IN:** If any customerId in Orders is NULL, `NOT IN` returns no rows for any customer. LEFT JOIN and NOT EXISTS do not have this problem.

## Worked Example

The anti-join pattern identifies rows in one table that have no matching row in another. The LEFT JOIN approach works by joining all customers to their orders, then filtering for the rows where the join produced no match (indicated by NULLs in the right side).

```
Customers table:
  id | name
  1  | Joe
  2  | Henry
  3  | Sam
  4  | Max

Orders table:
  id | customerId
  1  | 3
  2  | 1

LEFT JOIN Customers → Orders on id = customerId:
  Joe (1)   -> matches order 2   -> o.id = 2   (not NULL)
  Henry (2) -> no match          -> o.id = NULL
  Sam (3)   -> matches order 1   -> o.id = 1   (not NULL)
  Max (4)   -> no match          -> o.id = NULL

WHERE o.id IS NULL:
  Henry, Max

Result: Henry, Max
```

## Approaches

### Approach 1: LEFT JOIN + IS NULL

<details>
<summary>Explanation</summary>

Join Customers to Orders with LEFT JOIN. Customers with no orders get NULLs for all Orders columns. Filter for those NULLs.

```sql
SELECT c.name AS Customers
FROM Customers c
LEFT JOIN Orders o ON c.id = o.customerId
WHERE o.id IS NULL;
```

This is the most common anti-join pattern. Check the primary key column (o.id) for NULL, not the join key (o.customerId), because the join key could legitimately be NULL in the source data.

</details>

### Approach 2: NOT EXISTS

<details>
<summary>Explanation</summary>

For each customer, check whether a matching order exists.

```sql
SELECT name AS Customers
FROM Customers c
WHERE NOT EXISTS (
    SELECT 1 FROM Orders o WHERE o.customerId = c.id
);
```

NOT EXISTS is often more readable for anti-joins and avoids potential issues with duplicate matches. The optimizer typically produces the same plan as LEFT JOIN + IS NULL.

</details>

### Approach 3: NOT IN (with caveat)

<details>
<summary>Explanation</summary>

```sql
SELECT name AS Customers
FROM Customers
WHERE id NOT IN (SELECT customerId FROM Orders);
```

Simpler syntax but has a critical flaw: if any customerId in Orders is NULL, the entire NOT IN evaluates to UNKNOWN for every row, returning zero results. Always prefer LEFT JOIN + IS NULL or NOT EXISTS.

</details>

## Edge Cases

| Scenario | Expected | Why |
|---|---|---|
| All customers have orders | Empty result | No unmatched rows |
| No customers have orders | All customers returned | All rows are unmatched |
| Customer with multiple orders | Excluded | At least one match means not "never" |
| NULL customerId in Orders | NOT IN returns nothing; LEFT JOIN and NOT EXISTS work correctly | The NOT IN NULL trap |

## Interview Tips

> "I'll use a LEFT JOIN anti-join pattern: LEFT JOIN Orders on customerId, then WHERE o.id IS NULL to find customers with no match. I avoid NOT IN because if any customerId in Orders is NULL, NOT IN silently returns no rows."

**What the interviewer evaluates:** The NOT IN NULL trap is a classic interview gotcha. Mentioning it unprompted shows SQL depth and production experience. Most interviewers consider this a strong positive signal. If you use NOT IN, you should immediately note the NULL caveat and explain why you'd prefer NOT EXISTS or LEFT JOIN + IS NULL in production.

## At Scale

LEFT JOIN + IS NULL and NOT EXISTS typically produce identical query plans (anti-join operator). NOT IN can be slower because the optimizer may not convert it to an anti-join, instead materializing the subquery as a list and checking membership for each row.

For large tables, the anti-join is O(n + m) with a hash-based implementation: build a hash set from Orders(customerId) and probe with Customers(id). Rows not found in the hash set are returned.

In distributed engines, if Orders is small relative to Customers, a broadcast anti-join sends the Orders hash set to every node, avoiding a shuffle.

## DE Application

Anti-joins are one of the most common data quality operations:
- "Which expected daily partitions are missing?" (expected dates LEFT JOIN actual dates WHERE actual IS NULL)
- "Which customers in the CRM have no activity records?" (gap detection)
- "Which files in the manifest were not delivered?" (SLA monitoring)
- "Which dimension keys in the fact table have no matching dimension?" (referential integrity check)

Gap detection with anti-joins is a foundation of pipeline monitoring and data quality frameworks.

## Dialect Notes

Syntax is identical across all major engines. LEFT JOIN, NOT EXISTS and NOT IN are part of the SQL standard. The NULL behavior of NOT IN (three-valued logic) is universal and not dialect-specific.

## Related Problems

- [175. Combine Two Tables](175_combine_two_tables.md) - Basic LEFT JOIN
- [196. Delete Duplicate Emails](196_delete_duplicate_emails.md) - DELETE with subquery
