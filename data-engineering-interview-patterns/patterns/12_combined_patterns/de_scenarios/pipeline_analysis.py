"""
DE Scenario: Multi-pattern pipeline analysis.

Real-world application: analyzing a data pipeline to find bottlenecks,
compute critical path and identify the most error-prone tasks. Combines
hash maps (frequency counting), graphs (dependency traversal) and heaps
(priority-based processing).

Run: uv run python -m patterns.12_combined_patterns.de_scenarios.pipeline_analysis
"""

import heapq
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class TaskExecution:
    """A single task execution record."""

    task_name: str
    duration_seconds: float
    status: str  # success, failure, retry
    timestamp: str


def analyze_pipeline(
    tasks: list[dict],
    dependencies: list[tuple[str, str]],
    executions: list[TaskExecution],
) -> dict:
    """
    Comprehensive pipeline analysis combining three patterns.

    1. Hash Map: count error frequencies per task.
    2. Graph: build dependency graph, compute layers.
    3. Heap: find top-k slowest and most error-prone tasks.
    """
    # Phase 1: Hash Map - error frequency counting
    error_counts: dict[str, int] = defaultdict(int)
    total_counts: dict[str, int] = defaultdict(int)
    avg_durations: dict[str, list[float]] = defaultdict(list)

    for ex in executions:
        total_counts[ex.task_name] += 1
        avg_durations[ex.task_name].append(ex.duration_seconds)
        if ex.status == "failure":
            error_counts[ex.task_name] += 1

    error_rates = {
        task: error_counts[task] / total_counts[task]
        for task in total_counts
        if total_counts[task] > 0
    }

    avg_duration_map = {
        task: sum(durations) / len(durations)
        for task, durations in avg_durations.items()
    }

    # Phase 2: Graph - dependency analysis
    graph: dict[str, list[str]] = defaultdict(list)
    in_degree: dict[str, int] = defaultdict(int)
    task_names = {t["name"] for t in tasks}

    for task in task_names:
        in_degree.setdefault(task, 0)

    for parent, child in dependencies:
        graph[parent].append(child)
        in_degree[child] = in_degree.get(child, 0) + 1

    # Compute execution layers (topological order)
    layers: dict[str, int] = {}

    def get_layer(task: str, visited: set[str] | None = None) -> int:
        if task in layers:
            return layers[task]
        if visited is None:
            visited = set()
        if task in visited:
            return 0  # cycle protection
        visited.add(task)

        parents = [p for p, children in graph.items() if task in children]
        if not parents:
            layers[task] = 0
        else:
            layers[task] = 1 + max(get_layer(p, visited) for p in parents)
        return layers[task]

    for task in task_names:
        get_layer(task)

    # Phase 3: Heap - top-k analysis
    # Top 3 slowest tasks
    slowest = heapq.nlargest(
        3,
        avg_duration_map.items(),
        key=lambda x: x[1],
    )

    # Top 3 most error-prone tasks
    most_errors = heapq.nlargest(
        3,
        error_rates.items(),
        key=lambda x: x[1],
    )

    # Critical path (longest path through the DAG by duration)
    critical_path_duration = 0.0
    for task in task_names:
        layer = layers.get(task, 0)
        path_duration = sum(
            avg_duration_map.get(t, 0)
            for t, l in layers.items()
            if l <= layer
        )
        critical_path_duration = max(critical_path_duration, path_duration)

    return {
        "error_rates": dict(error_rates),
        "avg_durations": dict(avg_duration_map),
        "layers": dict(layers),
        "top_3_slowest": slowest,
        "top_3_error_prone": most_errors,
        "critical_path_duration": critical_path_duration,
        "total_tasks": len(task_names),
        "total_executions": len(executions),
    }


if __name__ == "__main__":
    import random

    print("=== Multi-Pattern Pipeline Analysis ===\n")

    tasks = [
        {"name": "extract_orders"},
        {"name": "extract_customers"},
        {"name": "extract_products"},
        {"name": "clean_orders"},
        {"name": "clean_customers"},
        {"name": "join_order_customer"},
        {"name": "aggregate_revenue"},
        {"name": "build_dashboard"},
    ]

    dependencies = [
        ("extract_orders", "clean_orders"),
        ("extract_customers", "clean_customers"),
        ("clean_orders", "join_order_customer"),
        ("clean_customers", "join_order_customer"),
        ("extract_products", "join_order_customer"),
        ("join_order_customer", "aggregate_revenue"),
        ("aggregate_revenue", "build_dashboard"),
    ]

    # Generate execution history
    executions = []
    base_durations = {
        "extract_orders": 30, "extract_customers": 15,
        "extract_products": 10, "clean_orders": 45,
        "clean_customers": 20, "join_order_customer": 120,
        "aggregate_revenue": 60, "build_dashboard": 25,
    }
    error_probs = {
        "extract_orders": 0.15, "clean_orders": 0.10,
        "join_order_customer": 0.20,
    }

    for run in range(100):
        for task in tasks:
            name = task["name"]
            duration = base_durations.get(name, 30) * random.uniform(0.8, 1.3)
            fail = random.random() < error_probs.get(name, 0.02)
            executions.append(TaskExecution(
                task_name=name,
                duration_seconds=duration,
                status="failure" if fail else "success",
                timestamp=f"2024-01-{15 + run // 10:02d}",
            ))

    result = analyze_pipeline(tasks, dependencies, executions)

    print("  Execution layers:")
    for layer_num in sorted(set(result["layers"].values())):
        layer_tasks = [t for t, l in result["layers"].items() if l == layer_num]
        print(f"    Layer {layer_num}: {layer_tasks}")

    print(f"\n  Top 3 slowest tasks:")
    for task, dur in result["top_3_slowest"]:
        print(f"    {task}: {dur:.1f}s avg")

    print(f"\n  Top 3 most error-prone:")
    for task, rate in result["top_3_error_prone"]:
        print(f"    {task}: {rate:.1%} failure rate")

    print(f"\n  Pipeline stats:")
    print(f"    Tasks: {result['total_tasks']}")
    print(f"    Total executions: {result['total_executions']}")
