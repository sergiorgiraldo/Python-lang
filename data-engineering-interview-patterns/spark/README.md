# Spark Patterns

How algorithmic patterns and SQL techniques look in PySpark. Every file shows the
connection between a pure Python solution from `patterns/` and its distributed
PySpark equivalent.

**15 Python files, 70 tests, 2 reference docs across 7 subsections.**

## Why Spark Knowledge Matters in DE Interviews

- Most data engineering roles involve Spark (or a similar distributed framework)
- Interview questions test whether you understand distribution, not just syntax
- Common pattern: "You solved this with a hash map. How would this work at 1TB?"
- The answer involves understanding shuffles, broadcasts, partitioning and data skew

## Structure

| Subsection | Pattern Connection | What You'll Learn |
|---|---|---|
| [01_joins](01_joins/) | [patterns/01_hash_map](../patterns/01_hash_map/) -> broadcast/shuffle joins | When to broadcast vs shuffle, skew handling |
| [02_sorting_and_merging](02_sorting_and_merging/) | [patterns/02_two_pointers](../patterns/02_two_pointers/) -> sort-merge joins | External sort, merge operations at scale |
| [03_window_functions](03_window_functions/) | [patterns/04_sliding_window](../patterns/04_sliding_window/) -> PySpark windows | Ranking, running aggregates, sessionization |
| [04_aggregations](04_aggregations/) | [patterns/05_heap_priority_queue](../patterns/05_heap_priority_queue/) -> groupBy, approx counting | GroupBy patterns, approximate algorithms |
| [05_partitioning](05_partitioning/) | [patterns/03_binary_search](../patterns/03_binary_search/) -> partition pruning | Repartition strategies, explain plans, optimization |
| [06_streaming](06_streaming/) | [patterns/04_sliding_window](../patterns/04_sliding_window/) -> Structured Streaming | Tumbling/sliding windows in streaming context |
| [reference](reference/) | Study aids | Cheatsheet and interview questions |

## Setup

```bash
# Install PySpark (optional dependency)
uv sync --extra spark

# Run Spark tests
uv run pytest spark/ -v

# Run without Spark (tests are skipped, not failed)
uv run pytest spark/ -v  # shows "skipped" if pyspark not installed
```

## How to Read Each File

1. Docstring explains the pattern connection
2. Pure Python function shows the algorithm
3. PySpark function shows the distributed equivalent
4. "Under the hood" comments explain what Spark does (shuffle, broadcast, etc.)
5. Tests verify both approaches produce the same result

## Key Concepts

- **Shuffles** - expensive network I/O when data moves between partitions
- **Broadcast joins** - sending small table to all workers to avoid shuffle
- **Partition strategies** - hash, range, round-robin
- **Data skew** - when one partition has much more data than others
- **Adaptive Query Execution** - Spark 3.x runtime optimization
- **Explain plans** - reading Spark's query plan to understand execution

## Reference Docs

- [Spark vs Python Cheatsheet](reference/spark_vs_python_cheatsheet.md) - translate Python patterns to PySpark
- [Common Interview Questions](reference/common_interview_questions.md) - top 20 PySpark questions with framework answers
