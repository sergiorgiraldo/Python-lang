# SQL Patterns for Data Engineering Interviews

## Overview

This section covers SQL patterns commonly tested in data engineering interviews. Each subsection focuses on a category of SQL techniques with LeetCode problems and production-oriented DE scenarios.

All problems are tested against DuckDB, an in-process analytical database that supports standard SQL with Postgres-like syntax. Solutions are written in portable SQL that works across most modern engines, with dialect-specific notes where syntax differs (BigQuery, Snowflake, Spark SQL, Postgres).

## How to Use

1. **Read the subsection README** to understand the SQL pattern category
2. **Try the problem** from the .md description before looking at the .sql solution
3. **Run the tests** to verify the solution: `uv run pytest sql/ -v`
4. **Study the DE scenarios** for production applications of each pattern
5. **Check dialect notes** if you're preparing for a specific platform

## Structure

Each problem has three files:

```
problems/
  176_second_highest_salary.sql    # The SQL solution
  176_second_highest_salary.md     # Problem description, worked example, approach
  176_second_highest_salary_test.py # Python test using DuckDB
```

Tests insert their own data inline so you can see input and expected output together.

## Subsections

| # | Section | Problems | Focus |
|---|---|---|---|
| 01 | [Window Functions](01_window_functions/) | 9 | RANK, ROW_NUMBER, LAG/LEAD, running aggregates |
| 02 | [Joins](02_joins/) | 8 | LEFT/INNER/SELF joins, anti-joins, MERGE |
| 03 | [Aggregations](03_aggregations/) | 5 | GROUP BY, HAVING, CASE, pivot, gap detection |
| 04 | [Recursive CTEs](04_recursive_ctes/) | 4 | Hierarchies, path enumeration, graph traversal |
| 05 | [Optimization & Production](05_optimization_and_production/) | - | EXPLAIN, anti-patterns, dialect comparison, advanced patterns |
| 06 | [dbt Patterns](06_dbt_patterns/) | - | Production dbt project: staging, intermediate, marts, macros |

## Running Tests

```bash
# All SQL tests
uv run pytest sql/ -v

# Specific subsection
uv run pytest sql/01_window_functions/ -v

# Specific problem
uv run pytest sql/01_window_functions/problems/176_second_highest_salary_test.py -v
```

## Connection to Patterns Section

SQL patterns connect to algorithmic patterns:

| SQL Pattern | Algorithmic Equivalent | Connection |
|---|---|---|
| Window functions (RANK, ROW_NUMBER) | Heap / sorting ([Pattern 05](../patterns/05_heap_priority_queue/README.md)) | Top-k selection, ordering |
| JOIN operations | Hash Map ([Pattern 01](../patterns/01_hash_map/README.md)) | Hash joins build a hash table internally |
| GROUP BY + HAVING | Hash Map counting | Frequency counting and filtering |
| Recursive CTEs | Graph/Tree traversal ([Pattern 06](../patterns/06_graph_topological_sort/README.md), [Pattern 10](../patterns/10_recursion_trees/README.md)) | BFS level-by-level |
| MERGE / upsert | Hash Map + conditional logic | Key-based lookup and update |

## DuckDB Notes

DuckDB supports most Postgres-compatible SQL including:
- Window functions with full frame specification
- CTEs (WITH) and recursive CTEs (WITH RECURSIVE)
- QUALIFY clause (filter after window functions - also supported in BigQuery/Snowflake)
- GROUPING SETS, ROLLUP, CUBE
- JSON functions
- EXPLAIN and EXPLAIN ANALYZE

Where DuckDB differs from other engines, dialect notes are included in the problem .md files.
