"""
DE Scenario: Cycle Detection in Pipeline Dependencies

Detect circular dependencies in pipeline configurations before
deployment. A cycle means the pipeline can never complete.
"""

from collections import defaultdict


def detect_cycles(
    tasks: list[str], dependencies: list[tuple[str, str]]
) -> dict[str, bool | list[list[str]]]:
    """
    Detect all cycles in a directed dependency graph.

    Uses 3-state DFS with path tracking to find and report
    actual cycle paths, not just "a cycle exists."

    Args:
        tasks: List of task names.
        dependencies: List of (dependency, task) pairs.

    Returns:
        Dict with 'has_cycle' (bool) and 'cycles' (list of cycles).
    """
    graph: dict[str, list[str]] = defaultdict(list)
    for dep, task in dependencies:
        graph[dep].append(task)

    # 0 = unvisited, 1 = in current path, 2 = done
    state: dict[str, int] = {t: 0 for t in tasks}
    path: list[str] = []
    cycles: list[list[str]] = []

    def dfs(node: str) -> None:
        if state.get(node) == 2:
            return
        if state.get(node) == 1:
            # Found cycle - extract it from path
            cycle_start = path.index(node)
            cycle = path[cycle_start:] + [node]
            cycles.append(cycle)
            return

        state[node] = 1
        path.append(node)

        for neighbor in graph[node]:
            dfs(neighbor)

        path.pop()
        state[node] = 2

    for task in tasks:
        if state[task] == 0:
            dfs(task)

    return {"has_cycle": len(cycles) > 0, "cycles": cycles}


def detect_cycle_kahn(
    tasks: list[str], dependencies: list[tuple[str, str]]
) -> dict[str, bool | list[str]]:
    """
    Detect if a cycle exists using Kahn's algorithm.

    Doesn't report the actual cycle path but is simpler.
    Unprocessed nodes after Kahn's are involved in cycles.

    Time: O(V + E)  Space: O(V + E)
    """
    from collections import deque

    graph: dict[str, list[str]] = defaultdict(list)
    in_degree: dict[str, int] = {t: 0 for t in tasks}

    for dep, task in dependencies:
        graph[dep].append(task)
        in_degree[task] = in_degree.get(task, 0) + 1

    queue = deque(t for t in tasks if in_degree[t] == 0)
    processed: set[str] = set()

    while queue:
        node = queue.popleft()
        processed.add(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    stuck = sorted(set(tasks) - processed)
    return {"has_cycle": len(stuck) > 0, "stuck_tasks": stuck}


if __name__ == "__main__":
    # Valid DAG
    print("Valid Pipeline")
    print("=" * 40)
    tasks = ["extract", "transform", "load", "validate", "report"]
    deps = [
        ("extract", "transform"),
        ("transform", "load"),
        ("load", "validate"),
        ("validate", "report"),
    ]
    result = detect_cycles(tasks, deps)
    print(f"Has cycle: {result['has_cycle']}")

    # Pipeline with cycle
    print("\nPipeline with Circular Dependency")
    print("=" * 40)
    tasks2 = ["ingest", "enrich", "validate", "clean", "publish"]
    deps2 = [
        ("ingest", "enrich"),
        ("enrich", "validate"),
        ("validate", "clean"),
        ("clean", "enrich"),  # circular: clean depends on enrich
        ("clean", "publish"),
    ]
    result2 = detect_cycles(tasks2, deps2)
    print(f"Has cycle: {result2['has_cycle']}")
    for cycle in result2["cycles"]:
        print(f"  Cycle: {' → '.join(cycle)}")

    # Kahn's approach
    print("\nKahn's Approach")
    kahn_result = detect_cycle_kahn(tasks2, deps2)
    print(f"Stuck tasks: {kahn_result['stuck_tasks']}")
