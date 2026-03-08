# Joins

Joins combine rows from two or more tables based on related columns. They are the most fundamental SQL operation for working with normalized data. Every data engineering pipeline, every analytics query and every reporting system relies on joins to connect related entities.

## Join Types

| Type | Keeps | Use When |
|---|---|---|
| INNER JOIN | Only matching rows from both sides | You need records that exist in both tables |
| LEFT JOIN | All left rows + matching right rows | Preserving completeness (all customers, even those without orders) |
| RIGHT JOIN | All right rows + matching left rows | Rarely used; rewrite as LEFT JOIN with tables swapped |
| FULL OUTER JOIN | All rows from both sides | Finding mismatches in both directions |
| CROSS JOIN | Every combination of left and right | Generating all pairs (calendar x products for coverage) |

**In practice:** INNER and LEFT cover 95% of use cases. RIGHT JOIN is almost always better expressed as LEFT JOIN. FULL OUTER is used for reconciliation. CROSS JOIN is rare and dangerous on large tables.

## Self-Joins

A self-join joins a table to itself. The same table plays two roles, distinguished by aliases.

```sql
SELECT e.name AS employee, m.name AS manager
FROM Employee e
JOIN Employee m ON e.managerId = m.id;
```

**When to use:** Any comparison between rows in the same table where the relationship is defined by a foreign key pointing back to the same table. Org charts, friend networks, bill-of-materials and reply threads all use self-joins.

## Anti-Join Patterns

Anti-joins find rows in one table with no match in another. Three syntaxes, same result:

```sql
-- LEFT JOIN + IS NULL (recommended)
SELECT c.name FROM Customers c
LEFT JOIN Orders o ON c.id = o.customerId
WHERE o.id IS NULL;

-- NOT EXISTS (also recommended)
SELECT name FROM Customers c
WHERE NOT EXISTS (SELECT 1 FROM Orders o WHERE o.customerId = c.id);

-- NOT IN (avoid: NULL trap)
SELECT name FROM Customers
WHERE id NOT IN (SELECT customerId FROM Orders);
```

**The NOT IN NULL trap:** If any value in the NOT IN subquery is NULL, the entire expression evaluates to UNKNOWN for every row, returning zero results. Always prefer LEFT JOIN + IS NULL or NOT EXISTS.

## Semi-Joins

Semi-joins return rows from the left table that have at least one match in the right table, without duplicating left rows. Use EXISTS:

```sql
SELECT c.name FROM Customers c
WHERE EXISTS (SELECT 1 FROM Orders o WHERE o.customerId = c.id);
```

Unlike INNER JOIN, EXISTS returns each customer at most once even if they have multiple orders. This avoids accidental row multiplication.

## Join Algorithms

Database engines use three main algorithms to execute joins:

### Nested Loop Join

```
For each row in left table:
    For each row in right table:
        If condition matches: output pair
```

- **Complexity:** O(n * m)
- **When chosen:** Small tables, or when an index on the inner table makes the inner loop O(log m) per probe
- **Memory:** O(1) (no buffer needed)

### Hash Join

```
Build phase: Hash the smaller table's join key into a hash table
Probe phase: For each row in the larger table, look up in hash table
```

- **Complexity:** O(n + m) expected
- **When chosen:** No useful index, medium to large tables, equi-join conditions
- **Memory:** O(min(n, m)) for the hash table

### Sort-Merge Join

```
Sort both tables by join key
Merge: walk through both sorted lists, matching equal keys
```

- **Complexity:** O(n log n + m log m) for sorting, O(n + m) for merge
- **When chosen:** Both inputs already sorted (from an index or prior ORDER BY), or for non-equi joins (range conditions)
- **Memory:** O(1) after sorting (streaming merge)

### How Indexes Affect the Choice

- **Index on join key:** Enables nested loop with index lookup (O(n * log m)), which beats hash join for small outer tables
- **Covering index:** The join can be resolved entirely from the index without touching the base table
- **No index:** Hash join is the default for equi-joins, sort-merge for range joins

## Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| INNER when LEFT needed | Missing rows in output | Use LEFT JOIN |
| Missing join condition | Accidental cross join (row explosion) | Always specify ON clause |
| COUNT(*) with LEFT JOIN | Counts NULLs (off-by-one for empty groups) | Use COUNT(column) |
| NOT IN with NULLs | Empty result set | Use NOT EXISTS or LEFT JOIN + IS NULL |
| Joining without dedup | Row multiplication | Dedup before joining or use EXISTS |
| Wrong table as left in LEFT JOIN | Wrong side preserved | Left table = the one you want to keep all rows from |

## Performance

**Join order:** The optimizer reorders joins to minimize intermediate result sizes. The "small table first" heuristic builds hash tables from smaller tables.

**Join key indexing:** An index on the join key of the probed (inner) table enables index-based nested loop joins. For hash joins, indexes are not used.

**Broadcast joins:** In distributed engines (Spark, BigQuery, Snowflake), if one table fits in memory, it is broadcast to every executor. This avoids shuffling the larger table.

**Partition alignment:** If both tables are partitioned by the join key, each partition pair can be joined independently without shuffling.

## At Scale

| Scale | Hash Join (equi) | Sort-Merge Join | Nested Loop (indexed) |
|---|---|---|---|
| 1M x 1M | < 1 second | 1-3 seconds | Depends on selectivity |
| 100M x 1M | 5-15 seconds | 10-30 seconds | Fast if outer is small |
| 1B x 1B | 1-5 minutes | 2-10 minutes | Impractical |

Hash joins dominate in warehouses. Sort-merge joins appear when data is pre-sorted or for range conditions. Nested loops are used for small-to-large lookups with indexes.

In distributed engines, the shuffle for hash joins is often the bottleneck. Reducing shuffle by co-partitioning tables or using broadcast joins is the primary optimization lever.

## Connection to Algorithmic Patterns

- **Hash Map (Pattern 01):** Hash joins build a hash map from the smaller table and probe it with the larger table. This is the exact same algorithm as the "two-sum" hash map pattern.
- **Two Pointers / Sort-Merge (Pattern 02):** Sort-merge joins sort both inputs and walk through them with two pointers. The merge step is identical to merging two sorted arrays.
- **Binary Search (Pattern 03):** Index-based nested loop joins perform a binary search (B-tree lookup) for each probe row.

## Problems

| # | Problem | Key Concept | Difficulty |
|---|---|---|---|
| [175](https://leetcode.com/problems/combine-two-tables/) | Combine Two Tables | LEFT JOIN basics | Easy |
| [181](https://leetcode.com/problems/employees-earning-more-than-their-managers/) | Employees Earning More | Self-join | Easy |
| [183](https://leetcode.com/problems/customers-who-never-order/) | Customers Who Never Order | Anti-join (LEFT JOIN + IS NULL) | Easy |
| [196](https://leetcode.com/problems/delete-duplicate-emails/) | Delete Duplicate Emails | DELETE with subquery | Easy |
| [262](https://leetcode.com/problems/trips-and-users/) | Trips and Users | Double join + conditional aggregation | Hard |
| [570](https://leetcode.com/problems/managers-with-at-least-five-direct-reports/) | Managers with 5 Reports | Self-join + GROUP BY + HAVING | Medium |
| [580](https://leetcode.com/problems/count-student-number-in-departments/) | Count Students per Dept | LEFT JOIN + COUNT(column) | Medium |
| [602](https://leetcode.com/problems/friend-requests-ii-who-has-the-most-friends/) | Friend Requests - Most Friends | UNION ALL + GROUP BY | Medium |

## DE Scenarios

| Scenario | Pattern | Production Use |
|---|---|---|
| Anti-Joins for Finding Gaps | LEFT JOIN + IS NULL, NOT EXISTS, NOT IN | Pipeline monitoring, data quality |
| Self-Joins for Hierarchies | Multi-level self-join | Org chart rollup, geographic aggregation |
| Incremental Load Detection | Source-target join comparison | CDC, daily warehouse loads |
| MERGE / Upsert Patterns | INSERT ON CONFLICT, MERGE | Dimension maintenance, SCD |
