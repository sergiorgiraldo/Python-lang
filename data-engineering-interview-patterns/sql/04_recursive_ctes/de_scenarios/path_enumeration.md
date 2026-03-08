# Path Enumeration

## Overview

Path enumeration builds the full path from root to each node in a hierarchy. The path is a string like "CEO / VP Engineering / Director Backend" that encodes the complete ancestry of a node. This is useful for display (breadcrumbs), subtree queries (WHERE path LIKE 'prefix%') and debugging hierarchical data.

## The Pattern

```sql
WITH RECURSIVE paths AS (
    -- Base case: root nodes have their own name as the path
    SELECT id, name, parent_id, name AS full_path
    FROM tree_table
    WHERE parent_id IS NULL

    UNION ALL

    -- Recursive case: concatenate parent path with child name
    SELECT t.id, t.name, t.parent_id,
           p.full_path || ' / ' || t.name
    FROM tree_table t
    JOIN paths p ON t.parent_id = p.id
)
SELECT * FROM paths;
```

The base case starts from root nodes (where parent_id IS NULL) and sets the path to just the node's name. Each recursive step appends the child's name to its parent's path using string concatenation.

## Materialized Path Pattern

Instead of computing paths on demand with a recursive CTE, store the full path as a column in the table:

```sql
ALTER TABLE org_chart ADD COLUMN materialized_path VARCHAR(1000);

-- After computing paths with the recursive CTE:
UPDATE org_chart SET materialized_path = paths.full_path
FROM paths WHERE org_chart.emp_id = paths.emp_id;
```

With materialized paths, subtree queries become simple LIKE queries without recursion:

```sql
-- All descendants of VP Engineering (no recursive CTE needed)
SELECT * FROM org_chart
WHERE materialized_path LIKE 'CEO / VP Engineering%';
```

### Trade-offs

| Aspect | Recursive CTE (on demand) | Materialized Path |
|---|---|---|
| Read speed | Slow (recursion every query) | Fast (indexed LIKE or prefix scan) |
| Write speed | No overhead | Must update paths when tree changes |
| Data freshness | Always current | Stale until recomputed |
| Storage | No extra storage | Extra column per row |
| Complexity | Query-time complexity | Schema + maintenance complexity |

Use materialized paths when reads vastly outnumber writes (e.g., category navigation on an e-commerce site). Use recursive CTEs when the hierarchy changes frequently or when you only traverse occasionally.

## Subtree Queries with Paths

Once paths are computed (or materialized), subtree queries use string prefix matching:

```sql
-- All nodes under "Electronics"
WHERE full_path LIKE 'Products / Electronics%'

-- Direct children only (one level deeper)
WHERE full_path LIKE 'Products / Electronics / %'
  AND full_path NOT LIKE 'Products / Electronics / % / %'
```

For large datasets, a prefix index on the path column makes these queries fast:

```sql
-- Postgres: text_pattern_ops index for LIKE prefix queries
CREATE INDEX idx_path ON org_chart (materialized_path text_pattern_ops);
```

## Dialect Notes

String concatenation syntax varies by engine:

| Engine | Syntax |
|---|---|
| Postgres, DuckDB | `path \|\| ' / ' \|\| name` |
| MySQL | `CONCAT(path, ' / ', name)` |
| BigQuery | `CONCAT(path, ' / ', name)` or `path \|\| ' / ' \|\| name` |
| Snowflake | `path \|\| ' / ' \|\| name` or `CONCAT(path, ' / ', name)` |
| SQL Server | `path + ' / ' + name` |

## At Scale

Path string length grows linearly with tree depth. For a 10-level hierarchy with average node names of 20 characters, paths are ~220 characters. For 50 levels, paths are ~1100 characters. VARCHAR limits and index size limits may apply for very deep hierarchies.

LIKE prefix queries on materialized paths with a proper index are O(log n + k) where k is the number of matching rows. Without an index, they are O(n) full table scans. For 10M-row hierarchies, the index is essential.

The recursive CTE to compute all paths visits every edge in the tree exactly once: O(n) total work. The string concatenation at each level creates new strings, so memory usage is O(n * average_path_length).

## Production Examples

- **Category breadcrumbs:** "Home > Electronics > Laptops > Gaming Laptops"
- **File system paths:** "/home/user/documents/report.pdf"
- **URL hierarchies:** "/api/v2/users/123/orders"
- **Data lineage paths:** "raw.events > staging.events_deduped > analytics.daily_active_users"
- **Permission scoping:** "org / team-backend / project-api" determines access level
