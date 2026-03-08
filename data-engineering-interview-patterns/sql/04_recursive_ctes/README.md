# Recursive CTEs

Recursive CTEs allow a query to reference itself, enabling iterative computation in SQL. They process hierarchies, graphs and sequences by starting from a base case and repeatedly applying a recursive step until no new rows are produced.

## WITH RECURSIVE Syntax

```sql
WITH RECURSIVE cte_name AS (
    -- Base case: anchor query (runs once)
    SELECT ...
    FROM source_table
    WHERE starting_condition

    UNION ALL

    -- Recursive case: references cte_name (runs repeatedly)
    SELECT ...
    FROM source_table
    JOIN cte_name ON parent_child_relationship
    WHERE termination_guard
)
SELECT * FROM cte_name;
```

**Base case:** The anchor query that produces the initial row set. Runs exactly once.

**Recursive case:** References the CTE by name. Runs repeatedly, with each iteration receiving only the rows produced by the previous iteration (not all accumulated rows). Stops when it returns zero rows.

**UNION ALL vs UNION:** UNION ALL keeps all rows (faster, allows duplicates). UNION deduplicates after each level (slower, but useful for graph reachability where duplicates mean cycles).

## Termination

Recursion stops automatically when the recursive step produces no new rows. This happens naturally for trees (leaf nodes have no children). For graphs with cycles, you must add explicit termination:

- **Depth limit:** `WHERE depth < 100` in the recursive case
- **Path tracking:** `WHERE NOT list_contains(path, next_node)` prevents revisiting nodes
- **UNION deduplication:** Stops when no new (unseen) rows are produced

Without termination guards on cyclic data, the query runs until the engine's recursion limit is hit (or runs out of memory).

## Cycle Detection

| Strategy | How | Pros | Cons |
|---|---|---|---|
| Depth limit | `WHERE depth < N` | Simple, cheap | May miss deep paths, may not detect cycles |
| Path array | Track visited in array column | Reliable, detects actual cycles | Memory-heavy for long paths |
| Visited set (UNION) | Use UNION instead of UNION ALL | Automatic dedup | Only works for reachability, not path queries |
| Engine-native | Postgres CYCLE clause | Clean syntax | Not portable |

## Common Patterns

### Hierarchy Traversal

The most common pattern. Traverse parent-child relationships (org charts, category trees, folder structures).

```sql
WITH RECURSIVE tree AS (
    SELECT id, parent_id, 1 AS depth FROM nodes WHERE parent_id = :root
    UNION ALL
    SELECT n.id, n.parent_id, t.depth + 1
    FROM nodes n JOIN tree t ON n.parent_id = t.id
)
SELECT * FROM tree;
```

### Path Enumeration

Build full paths from root to each node (e.g., "Electronics / Laptops / Gaming").

```sql
WITH RECURSIVE paths AS (
    SELECT id, name AS full_path FROM nodes WHERE parent_id IS NULL
    UNION ALL
    SELECT n.id, p.full_path || ' / ' || n.name
    FROM nodes n JOIN paths p ON n.parent_id = p.id
)
SELECT * FROM paths;
```

### BOM Explosion

Expand a product into all components, multiplying quantities across levels.

```sql
WITH RECURSIVE bom_exp AS (
    SELECT component_id, quantity AS total_qty FROM bom WHERE parent_id = :product
    UNION ALL
    SELECT b.component_id, e.total_qty * b.quantity
    FROM bom b JOIN bom_exp e ON b.parent_id = e.component_id
)
SELECT component_id, SUM(total_qty) FROM bom_exp GROUP BY component_id;
```

### Graph Traversal

BFS through a graph, tracking distance and path.

```sql
WITH RECURSIVE bfs AS (
    SELECT :start AS node, 0 AS dist, [:start] AS path
    UNION ALL
    SELECT e.dst, b.dist + 1, list_append(b.path, e.dst)
    FROM edges e JOIN bfs b ON e.src = b.node
    WHERE NOT list_contains(b.path, e.dst)
)
SELECT node, MIN(dist) FROM bfs GROUP BY node;
```

### Sequence Generation

Generate a series of values (dates, numbers). Often replaceable with GENERATE_SERIES.

```sql
WITH RECURSIVE dates AS (
    SELECT DATE '2024-01-01' AS dt
    UNION ALL
    SELECT dt + INTERVAL '1 day' FROM dates WHERE dt < DATE '2024-12-31'
)
SELECT * FROM dates;
```

## Performance Characteristics

Each recursion level is a separate query execution. This has implications:

| Characteristic | Impact |
|---|---|
| Per-level overhead | Fixed cost per level (query planning, materialization) |
| Level width | Wide levels (many rows) are processed efficiently (set-based) |
| Level depth | Deep recursion (100+ levels) is slow due to per-level overhead |
| Intermediate results | Each level materializes its output before the next level starts |
| Memory | Accumulated rows from all levels are held in memory (or spilled) |

**Rule of thumb:** Recursive CTEs work well for shallow, wide trees (5-10 levels, thousands of nodes per level). They struggle with deep, narrow paths (500 levels) or dense graphs (where row count explodes exponentially per level).

## When NOT to Use Recursive CTEs

| Scenario | Better Alternative |
|---|---|
| Fixed-depth hierarchy (always 3 levels) | Self-joins: simpler, faster, no recursion overhead |
| Large graphs (1M+ nodes, frequent queries) | Graph database (Neo4j) or graph frameworks (GraphFrames, NetworkX) |
| Simple sequences (date ranges, number series) | GENERATE_SERIES (native in Postgres, DuckDB, Snowflake) |
| Weighted shortest path | Application code (Dijkstra) or graph database |
| Real-time graph queries | Graph database with indexed traversal |

## At Scale

| Operation | 10K nodes | 100K nodes | 1M nodes |
|---|---|---|---|
| Hierarchy traversal (depth 5) | < 1 second | 1-5 seconds | 10-30 seconds |
| Full path enumeration | < 1 second | 2-10 seconds | 30-120 seconds |
| BOM explosion (depth 5, width 10) | < 1 second | Depends on explosion size | Minutes (output may be huge) |
| Connected components | < 1 second | 10-60 seconds | Minutes to hours |

Bottleneck is always the join at each recursion level. Indexing the join column (parent_id, src) is essential. For distributed engines, the recursive CTE may not parallelize well because each level depends on the previous one.

## Connection to Algorithmic Patterns

Recursive CTEs are BFS in SQL form. Each recursion level processes one "layer" of the graph/tree simultaneously. This maps directly to algorithmic patterns:

- **Pattern 06 (Graph/Topological Sort):** BFS, DFS (simulated), connected components, topological ordering all map to recursive CTEs. SQL processes level-by-level (natural BFS), not node-by-node.
- **Pattern 10 (Recursion/Trees):** Tree problems (height, subtree aggregation, ancestor queries) translate directly to recursive CTEs. Trees are acyclic, so cycle detection is not needed.
- **Pattern 04 (Sliding Window):** Sequence generation with recursive CTEs can model sliding window problems, though window functions are usually more appropriate.

The natural parallelism of recursive CTEs (all nodes at depth N processed simultaneously) makes them efficient for wide trees in distributed engines that can parallelize the join across partitions.

## Dialect Notes

| Engine | Recursive CTE Support | Notes |
|---|---|---|
| BigQuery | Yes | 500-level hard limit |
| Snowflake | Yes | Configurable depth limit |
| Postgres | Yes | work_mem affects performance, CYCLE clause for cycle detection |
| MySQL 8.0+ | Yes | CTE_MAX_RECURSION_DEPTH system variable (default 1000) |
| DuckDB | Yes | No hard limit, performance degrades with depth |
| Spark SQL | No | Use DataFrame operations or GraphFrames for recursive logic |
| SQLite | Yes (3.8.3+) | Limited by SQLITE_MAX_TRIGGER_DEPTH |

**Spark SQL workaround:** Since Spark does not support recursive CTEs, implement recursion with a loop in PySpark:

```python
# Pseudo-code for recursive traversal in PySpark
current_level = base_case_df
all_results = current_level
while current_level.count() > 0:
    next_level = current_level.join(edges_df, ...)
    all_results = all_results.union(next_level)
    current_level = next_level
```

## Problems

| # | Problem | Key Concept | Difficulty |
|---|---|---|---|
| [569](https://leetcode.com/problems/median-employee-salary/) | Median Employee Salary | ROW_NUMBER + COUNT for positional median | Hard |
| [571](https://leetcode.com/problems/find-median-given-frequency-of-numbers/) | Find Median Given Frequency | Cumulative frequency for median position | Hard |
| [579](https://leetcode.com/problems/find-cumulative-salary-of-an-employee/) | Cumulative Salary | ROWS BETWEEN frame + ROW_NUMBER exclusion | Hard |
| [618](https://leetcode.com/problems/students-report-by-geography/) | Students Report By Geography | ROW_NUMBER alignment + manual pivot | Hard |

## DE Scenarios

| Scenario | Pattern | Production Use |
|---|---|---|
| Hierarchy Traversal | WITH RECURSIVE + depth tracking | Org chart rollup, category trees |
| Path Enumeration | String concatenation in recursion | Breadcrumbs, data lineage paths |
| Bill of Materials | Quantity multiplication across levels | Supply chain, dependency resolution |
| Graph Traversal | BFS with cycle detection | Data lineage, impact analysis |
