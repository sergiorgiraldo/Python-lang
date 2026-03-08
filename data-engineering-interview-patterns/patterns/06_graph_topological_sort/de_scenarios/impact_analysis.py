"""
DE Scenario: Impact Analysis (Downstream Effects)

Given a data lineage graph, find all downstream tables affected
by a change to a source table. Uses BFS/DFS to traverse
the dependency graph forward from the changed table.
"""

from collections import defaultdict, deque


def find_downstream(
    lineage: dict[str, list[str]], changed_table: str
) -> dict[str, list[str] | dict[str, int]]:
    """
    Find all tables downstream of a changed table.

    Uses BFS to find all reachable nodes and their distance
    (number of hops) from the changed table.

    Args:
        lineage: Dict of table → list of tables it feeds into.
        changed_table: The table being modified.

    Returns:
        Dict with 'affected' (list) and 'distances' (dict of table→hops).
    """
    if changed_table not in lineage and changed_table not in {
        t for targets in lineage.values() for t in targets
    }:
        return {"affected": [], "distances": {}}

    # Build forward graph
    forward: dict[str, list[str]] = defaultdict(list)
    for src, targets in lineage.items():
        for target in targets:
            forward[src].append(target)

    visited: set[str] = set()
    distances: dict[str, int] = {}
    queue = deque([(changed_table, 0)])
    visited.add(changed_table)

    while queue:
        node, dist = queue.popleft()
        distances[node] = dist
        for neighbor in forward.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))

    # Remove the source itself from affected list
    affected = sorted(t for t in visited if t != changed_table)
    del distances[changed_table]

    return {"affected": affected, "distances": distances}


def find_upstream(lineage: dict[str, list[str]], table: str) -> list[str]:
    """
    Find all tables upstream of a given table (its dependencies).

    Traverses the graph backward.
    """
    reverse: dict[str, list[str]] = defaultdict(list)
    for src, targets in lineage.items():
        for target in targets:
            reverse[target].append(src)

    visited: set[str] = set()
    queue = deque([table])
    visited.add(table)

    while queue:
        node = queue.popleft()
        for neighbor in reverse.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return sorted(t for t in visited if t != table)


if __name__ == "__main__":
    # Simulate a data lineage graph
    lineage = {
        "raw_events": ["stg_events"],
        "raw_users": ["stg_users"],
        "stg_events": ["fct_sessions", "fct_pageviews"],
        "stg_users": ["dim_users"],
        "dim_users": ["fct_orders", "fct_sessions", "rpt_user_activity"],
        "fct_sessions": ["rpt_daily_summary", "rpt_user_activity"],
        "fct_pageviews": ["rpt_daily_summary"],
        "fct_orders": ["rpt_daily_summary", "rpt_revenue"],
    }

    # Scenario: raw_users schema changes
    print("Impact Analysis: raw_users schema change")
    print("=" * 50)
    result = find_downstream(lineage, "raw_users")
    print(f"Affected tables ({len(result['affected'])}):")
    for table in result["affected"]:
        dist = result["distances"][table]
        print(f"  {'  ' * dist}{table} ({dist} hop{'s' if dist != 1 else ''} away)")

    print("\nUpstream of rpt_daily_summary:")
    upstream = find_upstream(lineage, "rpt_daily_summary")
    for table in upstream:
        print(f"  {table}")
