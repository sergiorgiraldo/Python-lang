# Pipeline Execution Order

**Run it:** `uv run python -m patterns.06_graph_topological_sort.de_scenarios.pipeline_execution_order`

## Real-World Context

Every orchestration system solves this: given tasks with dependencies, find a valid execution order. Airflow does it when scheduling DAG runs. dbt does it when building models. Any build system (Make, Bazel, Gradle) does it when compiling dependencies.

The bonus insight is parallelism: tasks at the same topological level have no dependencies between them and can run concurrently. This is how dbt's `--threads` parameter and Airflow's `max_active_tasks` work.

## The Problem

Given a set of pipeline tasks and their dependencies, produce an execution order where every task runs after its dependencies. Identify which tasks can run in parallel.

## Worked Example

Determining the execution order of pipeline tasks with dependencies. This is a direct application of topological sort (Kahn's algorithm).

```
Pipeline tasks and dependencies:
  extract_users → transform_users → load_users
  extract_orders → transform_orders → load_orders
  transform_users → build_user_orders (needs both)
  transform_orders → build_user_orders
  build_user_orders → export_report

Topological sort:
  In-degree 0: [extract_users, extract_orders] → run in parallel
  After completion: [transform_users, transform_orders] → run in parallel
  After both transforms: [load_users, load_orders, build_user_orders]
    load_users and load_orders can run in parallel with build_user_orders
  After build_user_orders: [export_report]

Execution waves:
  Wave 1: extract_users, extract_orders (parallel)
  Wave 2: transform_users, transform_orders (parallel)
  Wave 3: load_users, load_orders, build_user_orders
  Wave 4: export_report

Same algorithm Airflow uses to schedule DAG tasks.
```

## Why Graphs

| Approach | Time | Handles Parallelism? |
|----------|------|---------------------|
| Brute force (scan for ready tasks) | O(V^2 + VE) | Yes but slow |
| Topological sort (Kahn's) | O(V + E) | Yes, naturally |

Kahn's algorithm processes nodes level by level. Each level is a set of tasks with no dependencies between them. This directly maps to parallel execution groups.

## Production Considerations

- **Partial failures:** If a task fails, its downstream tasks can't run. Production systems track which tasks are blocked vs ready.
- **Priority within levels:** Multiple tasks at the same level compete for worker slots. Airflow uses priority_weight to break ties.
- **Dynamic DAGs:** Tasks can be added or removed between runs. The topological sort must be recomputed each time.
- **Cross-DAG dependencies:** Airflow sensors and dbt source freshness checks handle dependencies between separate DAGs.

## Connection to LeetCode

Direct application of problem 210 (Course Schedule II). The "levels" extension maps to processing nodes in BFS rounds, which Kahn's algorithm does naturally.

## Benchmark

At 10K tasks in a linear chain, topological sort is 10-50x faster than brute force scanning. The gap grows with denser dependency graphs where the brute force approach rescans all tasks each round.
