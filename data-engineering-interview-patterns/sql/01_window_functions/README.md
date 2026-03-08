# Window Functions

Window functions compute values across a set of related rows without collapsing them into a single output row. Unlike GROUP BY (which reduces N rows to 1 per group), a window function preserves every row and adds computed columns. This makes them indispensable for ranking, running aggregates, row-to-row comparisons and gap detection.

## Anatomy of a Window Function

```sql
FUNC() OVER (
    PARTITION BY col1, col2       -- group rows (optional)
    ORDER BY col3                 -- sort within partition (required for most functions)
    ROWS BETWEEN ... AND ...      -- frame clause (optional)
)
```

**PARTITION BY** divides rows into independent groups. Each partition is processed separately. Omitting PARTITION BY treats the entire result set as one partition.

**ORDER BY** defines the row sequence within each partition. Required for ranking functions and LAG/LEAD. Optional for aggregate functions (without it, the aggregate covers the whole partition).

**Frame clause** limits which rows within the partition are included in the computation. Relevant for aggregate functions (SUM, AVG, COUNT). Not used by ranking functions or LAG/LEAD.

## Ranking Functions

| Function | Ties | Gaps | Use When |
|---|---|---|---|
| ROW_NUMBER() | Arbitrary tiebreak | Never | Deduplication (exactly one row per group) |
| RANK() | Same rank for ties | Yes (1,1,3) | Competition-style ranking |
| DENSE_RANK() | Same rank for ties | No (1,1,2) | Nth distinct value, top-N by distinct |

**When to use which:**
- **ROW_NUMBER** for dedup (need exactly 1 row per partition)
- **DENSE_RANK** for "Nth highest" or "top N distinct" (no gaps in rank sequence)
- **RANK** for competition ranking where tied positions skip the next rank

## Frame Types

| Frame | Meaning | Handles Gaps |
|---|---|---|
| ROWS | Count physical rows | No (counts rows regardless of values) |
| RANGE | Count by logical value | Yes (only rows within value distance) |
| GROUPS | Count distinct groups of tied values | N/A (rarely used) |

**When frame type matters:** For moving averages with date gaps, ROWS counts the preceding N physical rows (which might span more than N days), while RANGE counts by date distance (only days within the window). Use RANGE when the logical time window matters more than the row count.

## The Island Technique

The most important advanced window function technique. Identifies groups of consecutive qualifying rows.

```sql
-- id - ROW_NUMBER() is constant for consecutive qualifying rows
SELECT *, id - ROW_NUMBER() OVER (ORDER BY id) AS grp
FROM table
WHERE qualifying_condition
```

Why it works: consecutive qualifying rows have sequential ids and sequential row numbers. The difference between two sequential sequences is constant. A gap in qualifying rows changes the constant, creating a new group.

Applications: streak detection, session boundaries, consecutive failure monitoring.

## Common Patterns

| Pattern | Function | Example |
|---|---|---|
| Deduplication | ROW_NUMBER | Keep latest record per entity |
| Ranking | DENSE_RANK | Top N salaries per department |
| Row comparison | LAG / LEAD | Day-over-day change detection |
| Running total | SUM + frame | Cumulative revenue |
| Moving average | AVG + frame | 7-day rolling average |
| Streak detection | ROW_NUMBER (island) | Consecutive days above threshold |

## Performance

Window functions require sorting. The PARTITION BY + ORDER BY columns determine the sort key. Multiple window functions with the same PARTITION BY and ORDER BY share a single sort.

**Cost model:**
- Sort: O(n log n) per partition
- Window computation: O(n) per partition (single pass)
- Memory: O(partition_size) for the window buffer

**Optimization tips:**
- Align PARTITION BY with table partitioning to avoid shuffles in distributed engines
- Index the ORDER BY column for indexed-order scans on small result sets
- Multiple window functions with the same window specification share one sort pass
- Use QUALIFY (BigQuery, Snowflake, DuckDB) to avoid wrapping in a subquery

## Trade-offs: Window Functions vs Alternatives

| Approach | Pros | Cons |
|---|---|---|
| Window function | Single pass, flexible, readable | Requires sort, memory for buffer |
| Self-join | No window overhead | O(n^2) without index, assumes contiguous keys |
| Correlated subquery | No sort needed | O(n^2), hard to read |
| GROUP BY + JOIN back | Simple aggregation | Extra join, two passes |

Window functions are almost always the best choice for these patterns. Self-joins and correlated subqueries are legacy approaches that appear in older codebases but should not be the first choice in new SQL.

## At Scale

Concrete numbers for window function operations on modern warehouse engines:

| Scale | Dedup (ROW_NUMBER) | Ranking (DENSE_RANK) | Running Total (SUM) |
|---|---|---|---|
| 1M rows | < 1 second | < 1 second | < 1 second |
| 100M rows | 5-15 seconds | 5-15 seconds | 5-15 seconds |
| 1B rows | 1-5 minutes | 1-5 minutes | 1-5 minutes |

Bottleneck is always the sort. Distributed engines (Snowflake, BigQuery, Spark) parallelize the sort across nodes, scaling near-linearly with cluster size.

## Connection to Algorithmic Patterns

Window functions bridge SQL and algorithmic thinking:

- **Sorting (Pattern 02, 03):** Window functions require sorted input. Understanding sort complexity helps estimate query cost.
- **Heap / Top-K (Pattern 05):** DENSE_RANK for top-N is the SQL equivalent of a heap-based top-K selection.
- **Sliding Window (Pattern 04):** Moving averages and running totals are the SQL equivalent of the sliding window algorithm pattern.
- **Hash Map (Pattern 01):** PARTITION BY is implemented via hash partitioning in distributed engines, directly mapping to the hash map pattern.

## Problems

| # | Problem | Key Concept | Difficulty |
|---|---|---|---|
| [176](https://leetcode.com/problems/second-highest-salary/) | Second Highest Salary | DENSE_RANK, NULL handling | Easy |
| [177](https://leetcode.com/problems/nth-highest-salary/) | Nth Highest Salary | Parameterized DENSE_RANK | Medium |
| [178](https://leetcode.com/problems/rank-scores/) | Rank Scores | DENSE_RANK basics | Easy |
| [180](https://leetcode.com/problems/consecutive-numbers/) | Consecutive Numbers | LAG for adjacency | Medium |
| [184](https://leetcode.com/problems/department-highest-salary/) | Department Highest Salary | PARTITION BY | Medium |
| [185](https://leetcode.com/problems/department-top-three-salaries/) | Department Top Three Salaries | DENSE_RANK + PARTITION BY | Hard |
| [197](https://leetcode.com/problems/rising-temperature/) | Rising Temperature | LAG + date validation | Easy |
| [550](https://leetcode.com/problems/game-play-analysis-iv/) | Game Play Analysis IV | Anchor date + retention | Medium |
| [601](https://leetcode.com/problems/human-traffic-of-stadium/) | Human Traffic of Stadium | Island technique | Hard |

## DE Scenarios

| Scenario | Pattern | Production Use |
|---|---|---|
| Dedup with ROW_NUMBER | ROW_NUMBER + PARTITION BY | At-least-once ingestion cleanup |
| Running Totals | SUM with UNBOUNDED PRECEDING | Cumulative KPIs, financial reporting |
| Moving Averages | AVG with N PRECEDING | Trend detection, anomaly baselines |
| Sessionization | LAG + running SUM | Clickstream analysis, user sessions |
| Change Detection | LAG + CASE | SCD Type 2, audit trails |
