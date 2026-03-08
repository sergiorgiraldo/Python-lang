# Hierarchy Traversal

## Overview

Recursive CTEs traverse parent-child hierarchies by starting from a known set of rows (the base case) and repeatedly joining back to the source table to find the next level of children. Each recursion level processes one "layer" of the tree simultaneously. This is BFS (breadth-first search) expressed in SQL.

## The Pattern

```sql
WITH RECURSIVE descendants AS (
    -- Base case: starting nodes
    SELECT id, parent_id, 1 AS depth
    FROM tree_table
    WHERE parent_id = :start_node

    UNION ALL

    -- Recursive case: children of current level
    SELECT t.id, t.parent_id, d.depth + 1
    FROM tree_table t
    JOIN descendants d ON t.parent_id = d.id
)
SELECT * FROM descendants;
```

Three components define every recursive CTE:

1. **Base case:** the anchor query that returns the starting rows. This runs once.
2. **Recursive case:** references the CTE itself via JOIN. Runs repeatedly until it produces no new rows.
3. **Termination:** recursion stops automatically when the recursive step returns zero rows (leaf nodes have no children to find).

## Depth Tracking

Adding a `depth` column (incremented in the recursive step) enables level-aware queries:

- `WHERE depth <= 3` limits traversal to 3 levels deep
- `GROUP BY depth` counts nodes per level
- `MAX(depth)` finds the deepest path in the hierarchy

Depth tracking also serves as a safety mechanism. Setting `WHERE depth < 100` in the recursive case prevents runaway recursion if the data contains unexpected cycles.

## Cycle Detection

Circular references (A reports to B, B reports to A) cause infinite recursion. DuckDB has no built-in cycle detection for recursive CTEs. Two strategies:

**Path array:** Track visited nodes in an array column. Check membership before recursing.

```sql
WITH RECURSIVE reports AS (
    SELECT emp_id, name, manager_id, 1 AS depth,
           [emp_id] AS path
    FROM org_chart
    WHERE manager_id = :start

    UNION ALL

    SELECT o.emp_id, o.name, o.manager_id, r.depth + 1,
           list_append(r.path, o.emp_id)
    FROM org_chart o
    JOIN reports r ON o.manager_id = r.emp_id
    WHERE NOT list_contains(r.path, o.emp_id)
)
SELECT * FROM reports;
```

**Depth limit:** Add `WHERE r.depth < 50` to the recursive case. Simple but may miss deep legitimate hierarchies.

Postgres supports `CYCLE` detection syntax natively. BigQuery and Snowflake enforce hard depth limits (500 and configurable, respectively).

## At Scale

Recursion depth limits by engine:
- BigQuery: 500 levels (hard limit)
- Snowflake: configurable, default varies by query complexity
- Postgres: limited by work_mem and stack depth
- DuckDB: no hard limit, but performance degrades with depth

Performance characteristics:
- Each recursion level is a separate query execution (join + filter)
- Shallow, wide trees (5 levels, 10K nodes per level) are fast
- Deep, narrow trees (500 levels, 1 node per level) are slow due to per-level overhead
- Total work is O(levels * nodes_per_level * join_cost)

For hierarchies deeper than ~50 levels or with millions of nodes, consider materializing the hierarchy (closure table or nested set model) or using application-level traversal.

## When to Use Recursive CTE vs Alternatives

| Approach | Use When |
|---|---|
| Recursive CTE | Unknown depth, infrequent queries, moderate data size |
| Self-join (fixed depth) | Known, fixed depth (e.g., always 3 levels). Simpler and faster |
| Closure table | Frequent ancestor/descendant queries. Pre-materialized all-pairs paths |
| Nested set model | Read-heavy workloads with rare updates. Fast subtree queries |
| Application code | Complex traversal logic (conditional branching, pruning) |

## Production Examples

- **Org chart rollup:** total headcount and salary budget for a manager and all their reports
- **Data lineage traversal:** given a table, find all upstream sources and downstream consumers
- **Category hierarchy in e-commerce:** given "Electronics," find all subcategories (Laptops, Phones, Accessories, ...)
- **Permission inheritance:** a user inherits permissions from all parent groups in a group hierarchy

## Connection to Algorithmic Patterns

Recursive CTEs implement BFS in SQL. Each recursion level processes all nodes at that depth simultaneously, which maps to one "layer" of the BFS queue. This connects directly to:

- **Pattern 06 (Graph):** graph traversal algorithms (BFS, DFS) map to recursive CTE structure
- **Pattern 10 (Recursion/Trees):** tree problems often reduce to recursive CTE queries when the tree is stored in a database

The key difference from application-level BFS: SQL recursive CTEs process entire levels at once (set-based), while application BFS processes one node at a time (iterator-based). The set-based approach is more efficient when the data is in a database.
