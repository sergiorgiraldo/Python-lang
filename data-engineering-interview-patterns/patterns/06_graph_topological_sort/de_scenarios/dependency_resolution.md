# Dependency Resolution (dbt-style Model Ordering)

**Run it:** `uv run python -m patterns.06_graph_topological_sort.de_scenarios.dependency_resolution`

## Real-World Context

dbt projects have models that reference each other with `{{ ref('model_name') }}`. Before building, dbt must determine the order: which models have no dependencies (build first), which depend on those (build second), and so on. This is topological sort applied to SQL model dependencies.

## The Problem

Given a set of dbt models (SQL strings with ref() calls), parse the dependencies, detect cycles and produce a valid build order with parallel execution levels.

## Worked Example

Installing packages in the right order. If package A depends on B, B must be installed first. Topological sort over the dependency graph.

```
Dependencies:
  pandas → numpy, python-dateutil
  scikit-learn → numpy, scipy
  scipy → numpy
  python-dateutil → six

Graph (arrows mean "depends on"):
  pandas → numpy, python-dateutil → six
  scikit-learn → numpy, scipy → numpy

Topological sort:
  In-degree 0: [numpy, six] → install first
  After: python-dateutil→0, scipy→0 → install next
  After: pandas→0, scikit-learn→0 → install last

Install order: numpy, six, python-dateutil, scipy, pandas, scikit-learn

If there's a circular dependency (A needs B, B needs A),
topological sort detects it: not all packages reach in-degree 0.
```

## Why Graphs

dbt's ref() calls define directed edges between models. The set of models and their refs form a DAG (if valid). Topological sort gives the build order. If topological sort fails (output shorter than input), there's a circular reference.

## Production Considerations

- **Partial rebuilds:** dbt's `--select` flag runs a subset of models. The topological sort is filtered to only include selected models and their ancestors.
- **Incremental models:** Some models are incremental (append-only). They still need dependency ordering but process less data.
- **External dependencies:** `source()` references point outside the dbt project. These are always "already built" from the DAG's perspective.
- **Model selection syntax:** `dbt run --select model_a+` means "model_a and all its downstream dependencies." This is a graph traversal (BFS from model_a following edges forward).

## Connection to LeetCode

Combines ref() parsing (string pattern matching) with problem 210 (Course Schedule II) for ordering and problem 207 (Course Schedule) for cycle detection.

## Benchmark

For a project with 100+ models, topological sort completes in microseconds. The real bottleneck is the SQL compilation and database execution, not the dependency resolution.
