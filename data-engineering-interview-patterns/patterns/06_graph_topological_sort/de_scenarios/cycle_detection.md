# Cycle Detection in Pipeline Dependencies

**Run it:** `uv run python -m patterns.06_graph_topological_sort.de_scenarios.cycle_detection`

## Real-World Context

A misconfigured pipeline creates a circular dependency: table A depends on table B depends on table C depends on table A. The pipeline hangs forever. Detecting this before deployment saves hours of debugging.

Airflow prevents this at DAG parse time. dbt checks for ref() cycles during compilation. Any well-designed orchestration system validates the dependency graph before execution.

## The Problem

Given a set of tasks and their dependencies, determine if any circular dependencies exist. If so, report which tasks are involved and the specific cycle paths.

## Worked Example

Detecting circular dependencies in a pipeline DAG. If task A depends on B, B depends on C, and C depends on A, the pipeline can never execute.

```
Tasks and dependencies:
  ingest → clean → validate → publish
  validate → audit
  audit → clean  ← THIS CREATES A CYCLE

DFS with three-state coloring:
  Start at ingest (WHITE → GRAY)
    Visit clean (WHITE → GRAY)
      Visit validate (WHITE → GRAY)
        Visit publish (WHITE → GRAY → BLACK, leaf node)
        Visit audit (WHITE → GRAY)
          Visit clean → GRAY (already in progress)
          *** CYCLE DETECTED: clean → validate → audit → clean ***

Report: circular dependency involving [clean, validate, audit].
Pipeline cannot execute until this cycle is broken.
```

## Why Graphs

Cycle detection is fundamentally a graph problem. The two approaches each have tradeoffs:
- **DFS (3-state):** Reports actual cycle paths. Better for debugging.
- **Kahn's:** Reports which tasks are stuck. Simpler but doesn't show the cycle path directly.

## Production Considerations

- **Early detection:** Validate at configuration time (dbt compile, Airflow DAG parse) rather than at runtime. A cycle found during deployment is much cheaper than one found during execution.
- **Incremental validation:** When adding a new dependency, you only need to check if it creates a cycle from the new target back to the source. No need to re-validate the entire graph.
- **Soft dependencies:** Some systems have "soft" dependencies (nice to have, not required). These shouldn't be included in cycle detection.
- **Error messages:** Reporting the actual cycle path (not just "a cycle exists") helps the user fix the problem. "enrich → validate → clean → enrich" is actionable. "cycle detected" is not.

## Connection to LeetCode

Direct application of problem 207 (Course Schedule). The DFS approach extends it with path tracking to report the actual cycle. Kahn's approach identifies stuck nodes.

## Benchmark

Cycle detection is O(V + E) for both approaches. Even for large pipelines (thousands of tasks), this runs in milliseconds.
