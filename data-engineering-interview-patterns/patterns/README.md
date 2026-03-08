# Algorithm Patterns

Each pattern covers a fundamental approach that shows up in data engineering interviews. Patterns are organized by priority - start with Tier 1 and work through them in order.

## Where to Start

If you're short on time, start with [Hash Maps](01_hash_map/) - it's the most common pattern in coding interviews and the foundation for several others.

For a structured approach based on your timeline, see the [Learning Paths](../README.md#suggested-learning-paths) in the main README.

## Tier 1: Must Know

These patterns appear constantly. Master them first.

| # | Pattern | Problems | DE Scenarios | Focus |
|---|---------|----------|-------------|-------|
| 01 | [Hash Map](01_hash_map/) | 10 | 4 | O(1) lookup, counting, grouping |
| 02 | [Two Pointers](02_two_pointers/) | 9 | 4 | Sorted data, merging, partitioning |
| 03 | [Binary Search](03_binary_search/) | 8 | 4 | Sorted data, search space reduction |
| 04 | [Sliding Window](04_sliding_window/) | 8 | 4 | Subarray/substring problems |

## Tier 2: Important

These appear regularly. Cover them after Tier 1.

| # | Pattern | Problems | DE Scenarios | Focus |
|---|---------|----------|-------------|-------|
| 05 | [Heap / Priority Queue](05_heap_priority_queue/) | 6 | 4 | Top-K, merge K sorted |
| 06 | [Graph / Topological Sort](06_graph_topological_sort/) | 7 | 4 | Dependencies, DAGs |
| 07 | [Intervals](07_intervals/) | 6 | 4 | Overlaps, scheduling |
| 08 | [Stack](08_stack/) | - | - | Nested structures, monotonic patterns |
| 09 | [String Parsing](09_string_parsing/) | - | - | Log parsing, validation |

## Tier 3: Good to Know

Useful but less common in DE-specific interviews.

| # | Pattern | Problems | DE Scenarios | Focus |
|---|---------|----------|-------------|-------|
| 10 | [Recursion / Trees](10_recursion_trees/) | - | - | Hierarchies, CTEs |
| 11 | [Probabilistic Structures](11_probabilistic_structures/) | - | - | Bloom filters, HyperLogLog |
| 12 | [Combined Patterns](12_combined_patterns/) | - | - | Multi-pattern problems |

*Dash (-) indicates the pattern is planned but not yet built.*

## Supporting Resources

- [Pattern Recognition Cheat Sheet](../docs/PATTERN_RECOGNITION.md) - "If you see X, think Y"
- [Time Complexity Reference](../docs/TIME_COMPLEXITY_CHEATSHEET.md) - Big-O quick reference
- [Benchmarks](../benchmarks/) - Performance comparisons at scale
