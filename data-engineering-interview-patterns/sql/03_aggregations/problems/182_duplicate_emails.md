# Duplicate Emails (LeetCode #182)

🔗 [LeetCode 182: Duplicate Emails](https://leetcode.com/problems/duplicate-emails/)

> **Difficulty:** Easy | **Interview Frequency:** Very Common

## Problem Statement

Find all emails that appear more than once in the Person_Email table.

## Thought Process

1. **Group by email:** Collapse rows so that each unique email forms one group.
2. **Count per group:** COUNT(*) gives the number of rows sharing that email.
3. **Filter after aggregation:** HAVING COUNT(*) > 1 keeps only groups with duplicates. WHERE cannot reference aggregates.

## Worked Example

The query groups all rows by email and counts occurrences. HAVING acts as a post-aggregation filter, keeping only emails that appear more than once. This is the canonical "find duplicates" pattern in SQL.

```
Person_Email:
  id | email
  1  | a@b.com
  2  | c@d.com
  3  | a@b.com
  4  | d@e.com

GROUP BY email:
  a@b.com -> COUNT(*) = 2
  c@d.com -> COUNT(*) = 1
  d@e.com -> COUNT(*) = 1

HAVING COUNT(*) > 1:
  a@b.com qualifies (2 > 1)

Result: a@b.com
```

## Approaches

### Approach 1: GROUP BY + HAVING

<details>
<summary>Explanation</summary>

```sql
SELECT email
FROM Person_Email
GROUP BY email
HAVING COUNT(*) > 1;
```

GROUP BY collapses rows by email. HAVING filters groups after aggregation. This is the simplest and most efficient approach for finding duplicates when you only need the duplicate values (not the full rows).

</details>

### Approach 2: Self-Join

<details>
<summary>Explanation</summary>

```sql
SELECT DISTINCT a.email
FROM Person_Email a
JOIN Person_Email b ON a.email = b.email AND a.id <> b.id;
```

The self-join pairs every row with every other row sharing the same email. DISTINCT removes the duplicates from the output. This is less efficient than GROUP BY (it produces O(k^2) intermediate rows per k-duplicate group) but is useful when you need columns from both sides of the duplicate pair.

</details>

### Approach 3: Window Function

<details>
<summary>Explanation</summary>

```sql
SELECT DISTINCT email
FROM (
    SELECT email, COUNT(*) OVER (PARTITION BY email) AS cnt
    FROM Person_Email
) t
WHERE cnt > 1;
```

The window function computes a count per email without collapsing rows. This is useful when you need the full rows alongside the duplicate indicator. For this problem (returning only the email) it is overkill, but it transitions naturally to "show me all duplicate rows" follow-ups.

</details>

## Edge Cases

| Scenario | Expected | Why |
|---|---|---|
| No duplicates | Empty result | All groups have COUNT = 1 |
| All rows same email | That email returned once | GROUP BY collapses to one group |
| Email appears 3+ times | Returned once | GROUP BY + HAVING, not a counting query |
| Case sensitivity | 'a@b.com' and 'A@b.com' are distinct | DuckDB default collation is case-sensitive |
| Single row in table | Empty result | COUNT = 1 for the only group |

## Interview Tips

> "I'll GROUP BY email and use HAVING COUNT(*) > 1 to keep only emails that appear more than once. HAVING filters after grouping, while WHERE filters before. This is the standard duplicate detection pattern."

**What the interviewer evaluates:** This is the simplest aggregation problem. Clean and fast execution is expected. The interview value is in follow-ups: "now show me the full duplicate rows" (window function needed), "now delete the duplicates keeping the lowest id" (LC 196) or "how would you profile a table for duplicate keys?" (data quality application). Confusing WHERE with HAVING is a red flag.

## At Scale

GROUP BY with hash aggregation is O(n) in time. The hash table stores one entry per distinct email. For 1B rows with 100M unique emails, the hash table is roughly 2GB (email string + count per entry). This fits comfortably in memory for modern warehouses.

In distributed engines, the GROUP BY triggers a shuffle: all rows with the same email must land on the same node. If email has high cardinality, the shuffle distributes evenly. If a few emails dominate (hot keys), those partitions become bottlenecks.

**Dialect notes:** This query is identical across DuckDB, Postgres, BigQuery, Snowflake, MySQL and Spark SQL.

## DE Application

Duplicate detection is the first step in data quality profiling. Common production uses:

- "Find columns with duplicate values in what should be a unique key" (validation before loading)
- "Count duplicates per key to assess data freshness overlap" (incremental load debugging)
- "GROUP BY + HAVING COUNT > 1 on composite keys" (detecting fan-out issues after joins)
- "Automated data contract checks" (assert uniqueness constraints on ingested data)

This is the foundation of every data validation pipeline.

## Related Problems

- [196. Delete Duplicate Emails](../../02_joins/problems/196_delete_duplicate_emails.md) - Delete duplicates keeping lowest id
- [511. Game Play Analysis I](511_game_play_analysis_i.md) - GROUP BY + MIN aggregate
- [570. Managers with 5 Reports](../../02_joins/problems/570_managers_with_5_reports.md) - GROUP BY + HAVING with a threshold
