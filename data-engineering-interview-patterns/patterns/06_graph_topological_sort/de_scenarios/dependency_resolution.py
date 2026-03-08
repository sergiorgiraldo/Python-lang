"""
DE Scenario: Dependency Resolution (dbt-style model ordering)

Resolves dependencies between dbt models by parsing ref() calls
and producing a build order. Detects circular dependencies.
"""

import re
from collections import defaultdict, deque


def parse_model_refs(models: dict[str, str]) -> dict[str, list[str]]:
    """
    Extract ref() dependencies from model SQL.

    Args:
        models: Dict of model_name → SQL string.

    Returns:
        Dict of model_name → list of referenced model names.
    """
    refs: dict[str, list[str]] = {}
    for name, sql in models.items():
        # Match {{ ref('model_name') }}
        found = re.findall(r"\{\{\s*ref\(['\"](\w+)['\"]\)\s*\}\}", sql)
        refs[name] = found
    return refs


def resolve_build_order(
    models: dict[str, str],
) -> dict[str, list[str] | list[list[str]] | bool | list[str]]:
    """
    Determine build order for dbt models.

    Returns:
        Dict with 'order', 'levels', 'has_cycle', and 'cycle_models'.
    """
    refs = parse_model_refs(models)
    all_models = set(models.keys())

    graph: dict[str, list[str]] = defaultdict(list)
    in_degree: dict[str, int] = {m: 0 for m in all_models}

    for model, dependencies in refs.items():
        for dep in dependencies:
            if dep in all_models:
                graph[dep].append(model)
                in_degree[model] += 1

    queue = deque(m for m in all_models if in_degree[m] == 0)
    order: list[str] = []
    levels: list[list[str]] = []

    while queue:
        level = []
        for _ in range(len(queue)):
            model = queue.popleft()
            order.append(model)
            level.append(model)
            for neighbor in graph[model]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        levels.append(sorted(level))

    has_cycle = len(order) != len(all_models)
    cycle_models = [m for m in all_models if m not in set(order)] if has_cycle else []

    return {
        "order": order,
        "levels": levels,
        "has_cycle": has_cycle,
        "cycle_models": sorted(cycle_models),
    }


if __name__ == "__main__":
    # Simulate a dbt project
    models = {
        "stg_users": "SELECT * FROM {{ ref('raw_users') }}",
        "stg_orders": "SELECT * FROM {{ ref('raw_orders') }}",
        "raw_users": "SELECT * FROM source_users",
        "raw_orders": "SELECT * FROM source_orders",
        "dim_users": """
            SELECT u.*, o.order_count
            FROM {{ ref('stg_users') }} u
            LEFT JOIN (
                SELECT user_id, COUNT(*) as order_count
                FROM {{ ref('stg_orders') }}
                GROUP BY user_id
            ) o ON u.id = o.user_id
        """,
        "fct_orders": """
            SELECT o.*, u.segment
            FROM {{ ref('stg_orders') }} o
            JOIN {{ ref('dim_users') }} u ON o.user_id = u.id
        """,
        "rpt_revenue": """
            SELECT date, SUM(amount)
            FROM {{ ref('fct_orders') }}
            GROUP BY date
        """,
    }

    result = resolve_build_order(models)
    print("dbt Build Order")
    print("=" * 50)
    for i, level in enumerate(result["levels"]):
        print(f"  Level {i + 1}: {', '.join(level)}")
    print(f"\nHas cycle: {result['has_cycle']}")

    # Test with circular dependency
    print("\n--- Circular Dependency Test ---")
    circular_models = {
        "model_a": "SELECT * FROM {{ ref('model_c') }}",
        "model_b": "SELECT * FROM {{ ref('model_a') }}",
        "model_c": "SELECT * FROM {{ ref('model_b') }}",
    }
    result = resolve_build_order(circular_models)
    print(f"Has cycle: {result['has_cycle']}")
    print(f"Models in cycle: {result['cycle_models']}")
