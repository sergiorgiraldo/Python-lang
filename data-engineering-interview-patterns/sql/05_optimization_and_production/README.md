# SQL Part 5: Optimization and Production

Principal-level SQL skills that go beyond writing correct queries. This section
covers the difference between "can write SQL" and "can write efficient SQL and
explain why."

## Why This Section Exists

Parts 1-4 cover SQL correctness: window functions, joins, aggregations and
recursive CTEs. Those skills get you through the coding portion of an interview.

This section covers what comes after: optimization, cost awareness, dialect
differences and production patterns. At principal level, SQL interviews focus
on trade-offs and operational maturity, not just whether the query returns
the right answer.

## Contents

### Reference Documents (read these first)

Comprehensive guides covering optimization concepts and production SQL knowledge.

| Document | What It Covers |
|---|---|
| `reference/explain_plans.md` | How to read query plans, identify bottlenecks, dialect-specific EXPLAIN |
| `reference/anti_patterns.md` | 10 common performance anti-patterns with fixes |
| `reference/dialect_comparison.md` | Feature matrix across DuckDB, BigQuery, Snowflake, Spark SQL, Postgres |
| `reference/cost_aware_queries.md` | Cloud billing models, cost estimation, cost reduction techniques |

### Advanced Patterns (practice these)

Testable SQL patterns with `.sql` demonstrations, `.md` explanations and
`_test.py` verification.

| Pattern | Key Concept |
|---|---|
| `advanced_patterns/grouping_sets` | Multi-level aggregation in one pass (GROUPING SETS, ROLLUP, CUBE) |
| `advanced_patterns/qualify_clause` | Filter window function results without subqueries |
| `advanced_patterns/lateral_join` | Per-row subqueries for top-N-per-group and array flattening |
| `advanced_patterns/semi_structured_data` | JSON extraction, nested navigation, array unnesting |

### DE Scenarios (study these)

Production-oriented scenarios with optimization walkthroughs.

| Scenario | What It Demonstrates |
|---|---|
| `de_scenarios/query_optimization` | Step-by-step optimization of a query with 5 anti-patterns |
| `de_scenarios/partition_strategy` | Impact of partition filtering on query performance |
| `de_scenarios/materialized_views` | Pre-computation patterns: full refresh, incremental refresh |

## How to Use This Section

1. **Read the reference docs first.** They provide the conceptual foundation.
   Start with `explain_plans.md` and `anti_patterns.md`.
2. **Work through the advanced patterns.** Run the `.sql` files in DuckDB,
   read the `.md` explanations, then verify with the tests.
3. **Study the DE scenarios.** These simulate real production optimization
   tasks. Walk through each `.md` alongside its `.sql`.

## Running Tests

```bash
# Run all tests in this section
uv run pytest sql/05_optimization_and_production/ -v --tb=short

# Run a specific pattern's tests
uv run pytest sql/05_optimization_and_production/advanced_patterns/grouping_sets_test.py -v
```

## Key Takeaways

1. **Always check EXPLAIN before optimizing.** Measure first, then fix. Intuition
   about query performance is often wrong.
2. **Know the anti-patterns and their fixes.** SELECT *, DISTINCT as a band-aid,
   functions on indexed columns, missing partition filters.
3. **Understand cost implications of query design.** In cloud warehouses, every
   query has a dollar cost. Column pruning and partition pruning are the
   highest-impact optimizations.
4. **Know dialect differences for your target company.** QUALIFY, MERGE,
   LATERAL JOIN, recursive CTEs and JSON syntax all vary by engine.
5. **Use approximate functions when exact is not required.** APPROX_COUNT_DISTINCT
   on billions of rows is orders of magnitude cheaper than COUNT(DISTINCT).
6. **Think in terms of data volume and cost, not just correctness.** A correct
   query that scans 500GB when 2GB would suffice is a production problem.
