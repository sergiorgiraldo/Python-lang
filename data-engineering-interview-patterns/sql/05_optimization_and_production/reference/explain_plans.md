# EXPLAIN Plan Analysis

Reading query plans is the single most important optimization skill. Before tuning
any query, run EXPLAIN to understand what the engine does.

## What EXPLAIN Shows

A query plan is the sequence of physical operations the engine will perform to
execute your SQL. Each operation (node) in the plan shows:

- **Operator type**: scan, join, aggregate, sort, projection
- **Estimated row count**: how many rows the optimizer expects at each step
- **Cost estimate**: relative cost used by the optimizer to choose between plans

### Scan Types

| Scan Type | Description | When Used |
|---|---|---|
| Sequential Scan | Reads every row in the table | No usable index or filter matches most rows |
| Index Scan | Looks up rows via an index | Selective filter on indexed column |
| Bitmap Scan | Builds a bitmap from index then reads matching pages | Moderately selective filter |
| Filter | Post-scan row filtering | Conditions that cannot use an index |

### Join Algorithms

| Algorithm | How It Works | Best When |
|---|---|---|
| Hash Join | Builds hash table on smaller side, probes with larger | Equality joins, one side fits in memory |
| Sort-Merge Join | Sorts both sides, merges | Both sides already sorted or very large |
| Nested Loop | For each row in outer, scan inner | Small outer table or indexed inner lookup |

### Aggregation Strategies

| Strategy | How It Works | Best When |
|---|---|---|
| Hash Aggregation | Hash table on group keys | Many distinct groups, fits in memory |
| Sort Aggregation | Sort by group keys then scan | Data already sorted or too large for hash |

### Sort Operations

- **In-memory sort**: fast, preferred when data fits in memory
- **External sort (spill to disk)**: much slower, happens when sort exceeds memory budget

## Reading DuckDB EXPLAIN Output

DuckDB's EXPLAIN shows a tree of physical operators. The plan reads bottom-up:
the lowest node executes first, feeding results upward.

### Example 1: Simple Scan with Filter

```sql
CREATE TABLE Employee (
    id INTEGER, name VARCHAR, salary INTEGER, departmentId INTEGER
);

EXPLAIN SELECT id, name, salary FROM Employee WHERE salary > 100000;
```

Expected plan structure:
```
┌───────────────────────────┐
│       PROJECTION          │  -- Select specific columns
│   id, name, salary        │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         FILTER            │  -- WHERE salary > 100000
│   salary > 100000         │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│        SEQ_SCAN           │  -- Full table scan on Employee
│        Employee           │
└───────────────────────────┘
```

**What to notice**: DuckDB uses a sequential scan because there is no index.
In a columnar engine this is often acceptable since it only reads the requested
columns. The filter is applied after the scan.

### Example 2: Join Plan

```sql
CREATE TABLE Department (id INTEGER, name VARCHAR);

EXPLAIN SELECT e.name, d.name
FROM Employee e JOIN Department d ON e.departmentId = d.id;
```

Expected plan structure:
```
┌───────────────────────────┐
│       PROJECTION          │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│        HASH_JOIN          │  -- Build hash table on Department
│   e.departmentId = d.id   │
├─────────────┬─────────────┤
│  SEQ_SCAN   │  SEQ_SCAN   │
│  Employee   │  Department │
└─────────────┴─────────────┘
```

**What to notice**: DuckDB chooses a hash join. The smaller table (Department)
becomes the build side. The larger table (Employee) is the probe side.

### Example 3: Window Function Plan

```sql
EXPLAIN SELECT *, RANK() OVER (PARTITION BY departmentId ORDER BY salary DESC)
FROM Employee;
```

Expected plan structure:
```
┌───────────────────────────┐
│         WINDOW            │  -- RANK() computation
│   PARTITION BY deptId     │
│   ORDER BY salary DESC    │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│        SEQ_SCAN           │
│        Employee           │
└───────────────────────────┘
```

**What to notice**: the WINDOW operator requires sorting by (departmentId, salary).
DuckDB may show an explicit SORT node or fold the sort into the window operator.

### Example 4: Aggregation Plan

```sql
EXPLAIN SELECT departmentId, AVG(salary) FROM Employee GROUP BY departmentId;
```

Expected plan structure:
```
┌───────────────────────────┐
│     HASH_GROUP_BY         │  -- Group by departmentId
│   AVG(salary)             │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│        SEQ_SCAN           │
│        Employee           │
└───────────────────────────┘
```

**What to notice**: hash aggregation is the default for GROUP BY. If the number
of groups is very large relative to available memory, DuckDB may switch to an
external (spill-to-disk) strategy.

### EXPLAIN ANALYZE: Actual Execution Statistics

`EXPLAIN ANALYZE` runs the query and reports actual timings and row counts:

```sql
EXPLAIN ANALYZE SELECT departmentId, AVG(salary)
FROM Employee
GROUP BY departmentId;
```

This shows:
- **Actual rows** at each operator (vs estimated)
- **Execution time** per operator
- **Memory usage** for hash tables and sorts

Compare estimated vs actual rows. Large discrepancies indicate stale or missing
statistics, which cause the optimizer to choose suboptimal plans.

## What to Look for in Each Plan

### Red Flags

| Red Flag | What It Means | Likely Fix |
|---|---|---|
| Nested loop join on large tables | Missing join condition or missing index | Add proper join predicate or index |
| Full table scan on partitioned table | Missing partition filter in WHERE | Add filter on partition column |
| Sort spilling to disk | Data too large for in-memory sort | Increase memory or reduce sort size |
| Skewed hash join | One hash partition much larger than others | Use broadcast join or pre-filter skewed keys |
| Cartesian product | Accidental cross join | Check join conditions |
| Estimated rows far from actual | Stale statistics | Run ANALYZE or update statistics |

### Good Signs

- Index scans on selective filters
- Hash joins with reasonable build-side sizes
- Partition pruning reducing scan scope
- In-memory sorts (no spill)

## Dialect-Specific EXPLAIN

### BigQuery
EXPLAIN is not available as a SQL statement. Use the **Query Execution Details**
panel in the BigQuery console after running a query. Key metrics:
- **Bytes processed**: directly determines cost (on-demand pricing)
- **Slot usage**: compute consumption (flat-rate pricing)
- **Stages**: the query execution DAG showing shuffle, compute and output steps
- **Input/output rows per stage**: identifies where row explosion happens

### Snowflake
Use the **Query Profile** in the Snowflake web UI. Key things to check:
- **Partition pruning**: how many micro-partitions were scanned vs total
- **Spilling to local/remote storage**: indicates insufficient warehouse memory
- **Row explosion from joins**: large intermediate result sets
- **Percentage scanned from cache**: result cache and warehouse cache hits

### Postgres
```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) SELECT ...;
```
Shows actual timing, buffer hits vs reads (cache efficiency) and row counts.
Postgres plans are the most detailed of any engine. Look for:
- **Seq Scan** vs **Index Scan** on filtered tables
- **Buffers: shared hit** vs **shared read** (cache vs disk)
- **Sort Method: external merge** indicates spilling

### Spark SQL
```python
df.explain(True)       # Python API
# or
EXPLAIN EXTENDED ...;  # SQL API
```
Look for:
- **Exchange** operators (shuffles between executors)
- **BroadcastHashJoin** vs **SortMergeJoin** (broadcast avoids shuffle)
- **Partition pruning** on file-based tables (Parquet, Delta)
- **WholeStageCodegen**: Spark compiles query stages to Java bytecode

## Interview Context

At principal level, you may be asked to look at a slow query and diagnose it.
The ability to say "I would run EXPLAIN ANALYZE, look for full scans or
expensive sorts, check if the join is using hash or nested loop, and verify
partition pruning is happening" demonstrates operational maturity.

Follow this diagnostic workflow:
1. Run EXPLAIN ANALYZE on the slow query
2. Read the plan bottom-up, noting row counts at each step
3. Identify the most expensive operator (highest time or largest row explosion)
4. Check for red flags: full scans, spills, skew, cartesian products
5. Propose a targeted fix for the bottleneck
6. Re-run EXPLAIN ANALYZE to confirm improvement
