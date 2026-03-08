# Combine Two Tables (LeetCode #175)

🔗 [LeetCode 175: Combine Two Tables](https://leetcode.com/problems/combine-two-tables/)

> **Difficulty:** Easy | **Interview Frequency:** Very Common

## Problem Statement

Report the first name, last name, city and state for each person. If a person does not have an address, report NULL for city and state.

## Thought Process

1. **Which join type?** We need ALL persons in the output, even those without addresses. INNER JOIN would drop persons with no matching address. LEFT JOIN preserves every row from the left table (Person) and fills NULLs for unmatched right-side columns.
2. **Join key:** personId links the two tables. A person can have zero, one or many addresses.
3. **Column selection:** firstName and lastName from Person, city and state from Address. Use table aliases to avoid ambiguity.

## Worked Example

The core decision is LEFT vs INNER. LEFT JOIN guarantees that every person appears at least once, regardless of whether they have an address row. When Address has no match for a given personId, the join fills city and state with NULL.

```
Person table:
  personId | firstName | lastName
  1        | Allen     | Wang
  2        | Bob       | Alice

Address table:
  addressId | personId | city           | state
  1         | 2        | New York City  | New York

LEFT JOIN on personId:
  personId=1 (Allen): no match in Address -> city=NULL, state=NULL
  personId=2 (Bob): matches addressId=1 -> city='New York City', state='New York'

Result:
  firstName | lastName | city          | state
  Allen     | Wang     | NULL          | NULL
  Bob       | Alice    | New York City | New York
```

## Approaches

### Approach 1: LEFT JOIN

<details>
<summary>Explanation</summary>

Join Person to Address with LEFT JOIN on personId. This preserves all Person rows. Unmatched addresses produce NULLs.

```sql
SELECT p.firstName, p.lastName, a.city, a.state
FROM Person p
LEFT JOIN Address a ON p.personId = a.personId;
```

This is the only correct approach for this problem. INNER JOIN would silently drop persons without addresses.

**Dialect notes:** Identical across all engines. LEFT JOIN is part of the SQL standard and behaves the same in DuckDB, Postgres, MySQL, BigQuery, Snowflake and Spark SQL.

</details>

## Edge Cases

| Scenario | Expected | Why |
|---|---|---|
| Person with no address | NULL for city and state | LEFT JOIN preserves unmatched left rows |
| Person with multiple addresses | Multiple rows for that person | One row per matching address |
| Address with no matching person | Address row ignored | LEFT JOIN only preserves left table |
| Empty Address table | All persons with NULL city/state | No matches found |

## Interview Tips

> "This is a straightforward LEFT JOIN. I need all persons regardless of whether they have an address, so LEFT JOIN preserves the left table completely. INNER JOIN would incorrectly drop persons without addresses."

**What the interviewer evaluates:** This is a warm-up problem. A clean LEFT JOIN with correct column aliasing is expected in under a minute. Getting the join type wrong here (using INNER when LEFT is needed) is a serious red flag. The interviewer is checking that you understand the fundamental difference between INNER and LEFT JOIN before moving to harder problems.

## At Scale

LEFT JOIN with an index on the join key (personId) runs in O(n + m) where n is Person rows and m is Address rows. Without an index, the query optimizer typically picks a hash join: it builds a hash table from Address (usually the smaller table) and probes it with each Person row. Hash join is O(n + m) in time and O(m) in memory. For very large tables, the hash table may spill to disk.

In distributed engines (Spark, BigQuery), LEFT JOIN triggers a shuffle by join key. If one table is small enough, a broadcast join avoids the shuffle entirely: the small table is sent to every executor.

## DE Application

LEFT JOIN is the core of star schema queries. Fact tables join to dimension tables with LEFT JOIN so that fact rows without matching dimensions produce NULLs rather than disappearing. "Enrich orders with customer details" is the same structure as this problem: LEFT JOIN orders to customers on customer_id, accepting that some orders may have unknown customers (NULL enrichment fields). In data quality checks, those NULLs become signals for missing dimension records.

## Related Problems

- [183. Customers Who Never Order](183_customers_who_never_order.md) - LEFT JOIN + IS NULL (anti-join)
- [580. Count Student Number in Departments](580_count_students_per_dept.md) - LEFT JOIN + COUNT
