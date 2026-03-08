# Delete Duplicate Emails (LeetCode #196)

🔗 [LeetCode 196: Delete Duplicate Emails](https://leetcode.com/problems/delete-duplicate-emails/)

> **Difficulty:** Easy | **Interview Frequency:** Common

## Problem Statement

Delete all duplicate email entries, keeping only the row with the smallest id for each email.

## Thought Process

1. **DELETE vs SELECT:** This problem modifies data, which is unusual for interview SQL problems. The logic is the same as dedup-by-SELECT, but the output is the mutation itself.
2. **Identify keepers:** GROUP BY email, take MIN(id) for each group. These are the rows to keep.
3. **Delete the rest:** DELETE WHERE id NOT IN (keepers) or use ROW_NUMBER to mark duplicates.
4. **Production mindset:** In real pipelines, "delete duplicates" is usually "SELECT deduplicated rows INTO a new table, then swap." Direct DELETE on large tables is expensive.

## Worked Example

The approach is to first identify which rows to keep (the smallest id per email), then delete everything else. The GROUP BY + MIN(id) subquery produces exactly one id per distinct email. Any row whose id is not in that set is a duplicate.

```
Person_Email table:
  id | email
  1  | john@example.com
  2  | bob@example.com
  3  | john@example.com

Step 1 - Find keepers:
  SELECT MIN(id), email FROM Person_Email GROUP BY email
  -> (1, john@example.com), (2, bob@example.com)

Step 2 - Delete non-keepers:
  DELETE WHERE id NOT IN (1, 2)
  -> Deletes id=3

Remaining:
  id | email
  1  | john@example.com
  2  | bob@example.com
```

## Approaches

### Approach 1: DELETE with GROUP BY Subquery

<details>
<summary>Explanation</summary>

Find the minimum id per email, then delete rows not in that set.

```sql
DELETE FROM Person_Email
WHERE id NOT IN (
    SELECT MIN(id)
    FROM Person_Email
    GROUP BY email
);
```

Simple and readable. The subquery returns one id per distinct email (the smallest). All other rows are deleted.

</details>

### Approach 2: DELETE with ROW_NUMBER

<details>
<summary>Explanation</summary>

Use ROW_NUMBER to rank duplicates within each email group, then delete rows with rank > 1.

```sql
DELETE FROM Person_Email
WHERE id IN (
    SELECT id FROM (
        SELECT id,
               ROW_NUMBER() OVER (PARTITION BY email ORDER BY id) AS rn
        FROM Person_Email
    ) t
    WHERE rn > 1
);
```

More flexible than GROUP BY + MIN. By changing ORDER BY, you can keep the latest row instead of the first. By changing PARTITION BY, you can handle composite dedup keys.

</details>

## Edge Cases

| Scenario | Expected | Why |
|---|---|---|
| No duplicates | Nothing deleted | All ids are in the MIN set |
| All same email | Keep only smallest id | One group, one MIN |
| Non-sequential ids | Still keeps the smallest | MIN works on value, not position |
| Single row | Nothing deleted | Trivially unique |

## Interview Tips

> "I'll find the minimum id per email with GROUP BY, then DELETE rows not in that set. In production, I'd avoid DELETE on large tables and instead SELECT DISTINCT INTO a new table and swap, since DELETE has write amplification and transaction log overhead."

**What the interviewer evaluates:** The jump from SELECT-based dedup (ROW_NUMBER with WHERE rn = 1) to DELETE-based dedup tests whether you can adapt window function patterns to DML. Mentioning that production dedup uses INSERT...SELECT rather than DELETE shows pipeline experience. Knowing about MERGE/upsert as the incremental alternative is a strong signal.

## At Scale

DELETE on a large table is expensive:
- **Write amplification:** Each deleted row generates a write to the transaction log
- **Lock contention:** Large DELETEs may hold table-level locks for extended periods
- **MVCC overhead:** Deleted rows are marked, not removed, requiring later VACUUM/compaction

Production alternatives:
- **INSERT...SELECT:** Create a clean table from a deduplicated SELECT, then swap (rename) tables. No DELETE, no lock contention.
- **MERGE/upsert:** For incremental pipelines, use MERGE to insert new records and update existing ones without ever creating duplicates.
- **Partition-level replace:** In partitioned tables, overwrite the partition with deduplicated data instead of row-level DELETE.

For 1B rows with 10% duplicates, DELETE would modify 100M rows. INSERT...SELECT scans once and writes 900M rows to a new table, which is typically faster and avoids locking the original table.

## DE Application

Dedup is one of the most frequent operations in data engineering:
- **At-least-once delivery cleanup:** Kafka, Kinesis and Pub/Sub guarantee at-least-once, producing duplicates that must be removed downstream
- **Migration cleanup:** Historical data often contains duplicates from legacy systems
- **MERGE staging:** Dedup staging tables before MERGE INTO the target to avoid constraint violations
- **SCD maintenance:** When building slowly changing dimensions, dedup source snapshots before applying changes

The ROW_NUMBER approach is more production-friendly because it generalizes to composite keys and flexible ordering (keep latest vs keep first).

## Dialect Notes

DELETE syntax varies significantly across engines:

- **DuckDB / Postgres**: `DELETE FROM t USING ...` or `DELETE FROM t WHERE id IN (subquery)`. CTEs in DELETE are supported.
- **MySQL**: does not support CTEs in DELETE (before 8.0). Self-referencing subqueries in DELETE require wrapping in an extra subquery layer.
- **BigQuery**: `DELETE FROM t WHERE ...` with subquery. No USING clause.
- **Snowflake**: supports `DELETE FROM t USING ...` and CTEs in DELETE.
- **Spark SQL**: DELETE is only supported on Delta Lake tables, not standard Spark tables.

The ROW_NUMBER approach for identifying duplicates is identical across all engines. Only the DELETE execution syntax differs.

## Related Problems

- [176. Second Highest Salary](../01_window_functions/problems/176_second_highest_salary.md) - ROW_NUMBER/DENSE_RANK ranking
- [183. Customers Who Never Order](183_customers_who_never_order.md) - Subquery patterns
