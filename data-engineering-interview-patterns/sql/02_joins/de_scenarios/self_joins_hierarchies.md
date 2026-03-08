# Self-Joins for Hierarchies

## Overview

Organizations, file systems, product categories and geographic regions all form hierarchies stored as parent-child references in a single table. Self-joins navigate these hierarchies by joining the table to itself at each level.

## The Pattern

```sql
-- Two-level self-join: entity -> parent -> grandparent
SELECT e.name AS employee,
       m.name AS manager,
       d.name AS director
FROM org_chart e
LEFT JOIN org_chart m ON e.manager_id = m.emp_id
LEFT JOIN org_chart d ON m.manager_id = d.emp_id;
```

Each LEFT JOIN adds one level of hierarchy. LEFT JOIN (not INNER) preserves entities at the top of the hierarchy who have no parent.

## Fixed Depth vs Arbitrary Depth

**Self-join (fixed depth):**
- Known, shallow hierarchy (2-3 levels)
- Simple syntax, easy to understand
- Each level requires an additional JOIN
- Adding a level means changing the query

**Recursive CTE (arbitrary depth):**
```sql
WITH RECURSIVE chain AS (
    SELECT emp_id, name, manager_id, 1 AS depth
    FROM org_chart
    WHERE manager_id IS NULL

    UNION ALL

    SELECT e.emp_id, e.name, e.manager_id, c.depth + 1
    FROM org_chart e
    JOIN chain c ON e.manager_id = c.emp_id
)
SELECT * FROM chain ORDER BY depth, name;
```

Use recursive CTEs when:
- The hierarchy depth varies or is unknown
- You need the full path from root to leaf
- The data might have new levels added over time

## When Self-Join is Sufficient

Self-joins work well for:
- **Org charts with known levels:** CEO -> VP -> Director -> Manager -> IC (5 levels, 4 joins)
- **Geographic rollups:** City -> State -> Country (3 levels, 2 joins)
- **Product categories:** SKU -> Subcategory -> Category (3 levels, 2 joins)
- **Time hierarchies:** Day -> Month -> Quarter -> Year (fixed by definition)

## Production Example: Manager Chain Rollup

```sql
-- Roll up headcount to each level of management
SELECT d.name AS director,
       d.emp_id AS director_id,
       COUNT(DISTINCT m.emp_id) AS managers_under,
       COUNT(DISTINCT e.emp_id) AS total_reports
FROM org_chart d
LEFT JOIN org_chart m ON m.manager_id = d.emp_id
LEFT JOIN org_chart e ON e.manager_id = m.emp_id
WHERE d.manager_id IS NULL  -- top-level only
   OR d.title LIKE '%VP%'
GROUP BY d.emp_id, d.name;
```

## At Scale

Self-joins multiply the data at each level. For n employees with k levels:
- 1 level: n rows
- 2 levels: up to n^2 in the worst case (flat hierarchy), typically O(n) for tree structures
- k levels: O(n * branching_factor^(k-1))

For deep or wide hierarchies, recursive CTEs are more efficient because they traverse level by level instead of joining the full table at each level.

Materialized path (storing the full path as a string like "/1/2/4/6") or nested sets (storing left/right boundaries) are alternative data models that avoid self-joins entirely. They trade write complexity for read performance.

## Cycle Detection

Self-referencing data can contain cycles (A reports to B, B reports to A). Self-joins with a fixed number of levels handle this safely because the query has finite depth. Recursive CTEs need explicit cycle detection:

```sql
WITH RECURSIVE chain AS (
    SELECT emp_id, name, ARRAY[emp_id] AS path
    FROM org_chart WHERE manager_id IS NULL

    UNION ALL

    SELECT e.emp_id, e.name, c.path || e.emp_id
    FROM org_chart e
    JOIN chain c ON e.manager_id = c.emp_id
    WHERE e.emp_id != ALL(c.path)  -- cycle guard
)
SELECT * FROM chain;
```

## Common Applications

- **Org chart reporting:** Employee count per manager at each level
- **Cost center rollup:** Budget allocated to departments rolling up to divisions
- **Geographic aggregation:** Store revenue rolling up to region, then country
- **Bill of materials:** Component cost rolling up through assemblies
