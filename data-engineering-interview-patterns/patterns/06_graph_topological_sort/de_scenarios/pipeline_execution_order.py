"""
DE Scenario: Pipeline Execution Order (Topological Sort)

Given a set of pipeline tasks with dependencies, determine a valid
execution order using topological sort. Also identifies which tasks
can run in parallel (same topological level).
"""

import time
from collections import defaultdict, deque


def build_execution_plan(
    tasks: list[str], dependencies: list[tuple[str, str]]
) -> dict[str, list[list[str]]]:
    """
    Build a parallel execution plan from task dependencies.

    Args:
        tasks: List of task names.
        dependencies: List of (dependency, task) pairs meaning
            dependency must complete before task starts.

    Returns:
        Dict with 'order' (flat list), 'levels' (parallel groups),
        and 'has_cycle' (bool).
    """
    graph: dict[str, list[str]] = defaultdict(list)
    in_degree: dict[str, int] = {task: 0 for task in tasks}

    for dep, task in dependencies:
        graph[dep].append(task)
        in_degree[task] = in_degree.get(task, 0) + 1

    queue = deque(t for t in tasks if in_degree[t] == 0)
    order: list[str] = []
    levels: list[list[str]] = []

    while queue:
        level_size = len(queue)
        level: list[str] = []
        for _ in range(level_size):
            task = queue.popleft()
            order.append(task)
            level.append(task)
            for neighbor in graph[task]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        levels.append(level)

    has_cycle = len(order) != len(tasks)
    return {"order": order, "levels": levels, "has_cycle": has_cycle}


def brute_force_execution_plan(
    tasks: list[str], dependencies: list[tuple[str, str]]
) -> list[str]:
    """
    Brute force: repeatedly find tasks with all deps satisfied.

    Time: O(V^2 + V*E) - scan all tasks each round
    """
    completed: set[str] = set()
    dep_map: dict[str, set[str]] = defaultdict(set)
    for dep, task in dependencies:
        dep_map[task].add(dep)

    order: list[str] = []
    remaining = set(tasks)

    while remaining:
        ready = [t for t in remaining if dep_map[t].issubset(completed)]
        if not ready:
            return []  # cycle
        for task in sorted(ready):  # sort for deterministic order
            order.append(task)
            completed.add(task)
            remaining.remove(task)

    return order


if __name__ == "__main__":
    # Simulate a realistic dbt-like DAG
    tasks = [
        "raw_events",
        "raw_users",
        "raw_orders",
        "stg_events",
        "stg_users",
        "stg_orders",
        "dim_users",
        "fct_orders",
        "fct_sessions",
        "rpt_daily_summary",
        "rpt_user_activity",
    ]
    deps = [
        ("raw_events", "stg_events"),
        ("raw_users", "stg_users"),
        ("raw_orders", "stg_orders"),
        ("stg_users", "dim_users"),
        ("stg_orders", "fct_orders"),
        ("stg_events", "fct_sessions"),
        ("dim_users", "fct_orders"),
        ("dim_users", "fct_sessions"),
        ("fct_orders", "rpt_daily_summary"),
        ("fct_sessions", "rpt_daily_summary"),
        ("dim_users", "rpt_user_activity"),
        ("fct_sessions", "rpt_user_activity"),
    ]

    result = build_execution_plan(tasks, deps)
    print("Pipeline Execution Plan")
    print("=" * 50)
    for i, level in enumerate(result["levels"]):
        print(f"  Level {i + 1} (parallel): {', '.join(level)}")
    print(f"\nTotal levels: {len(result['levels'])}")
    print(f"Has cycle: {result['has_cycle']}")

    # Benchmark
    for n_tasks in [100, 1_000, 10_000]:
        task_list = [f"task_{i}" for i in range(n_tasks)]
        dep_list = [(f"task_{i}", f"task_{i + 1}") for i in range(n_tasks - 1)]

        start = time.perf_counter()
        build_execution_plan(task_list, dep_list)
        topo_time = time.perf_counter() - start

        start = time.perf_counter()
        brute_force_execution_plan(task_list, dep_list)
        brute_time = time.perf_counter() - start

        print(
            f"\nn={n_tasks:,}: topo={topo_time:.4f}s, brute={brute_time:.4f}s, "
            f"speedup={brute_time / topo_time:.1f}x"
        )
