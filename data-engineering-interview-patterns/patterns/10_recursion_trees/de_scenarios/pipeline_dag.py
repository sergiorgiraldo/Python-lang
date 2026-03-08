"""
DE Scenario: Pipeline DAG analysis (upstream/downstream discovery).

Real-world application: data lineage, impact analysis, dependency
tracking. "If this source table changes, what dashboards are affected?"
"What are all the upstream dependencies of this report?"

This is a directed acyclic graph (DAG) but uses the same recursive
traversal concepts as tree problems.

Run: uv run python -m patterns.10_recursion_trees.de_scenarios.pipeline_dag
"""

from __future__ import annotations

from dataclasses import dataclass, field
from collections import deque


@dataclass
class PipelineNode:
    """A node in a data pipeline DAG."""

    name: str
    node_type: str  # source, transform, model, report
    downstream: list[PipelineNode] = field(default_factory=list)
    upstream: list[PipelineNode] = field(default_factory=list)


def build_pipeline_dag(
    nodes: list[dict], edges: list[tuple[str, str]]
) -> dict[str, PipelineNode]:
    """Build a pipeline DAG from node definitions and edges."""
    node_map: dict[str, PipelineNode] = {}

    for n in nodes:
        node_map[n["name"]] = PipelineNode(
            name=n["name"],
            node_type=n["type"],
        )

    for source, target in edges:
        node_map[source].downstream.append(node_map[target])
        node_map[target].upstream.append(node_map[source])

    return node_map


def find_all_downstream(node: PipelineNode) -> list[str]:
    """
    Find all nodes downstream of a given node (impact analysis).

    "If raw_orders changes, what's affected?"

    BFS to avoid visiting the same node twice (DAGs can have
    multiple paths to the same node).
    """
    visited: set[str] = set()
    result: list[str] = []
    queue = deque(node.downstream)

    while queue:
        current = queue.popleft()
        if current.name in visited:
            continue
        visited.add(current.name)
        result.append(current.name)
        queue.extend(current.downstream)

    return result


def find_all_upstream(node: PipelineNode) -> list[str]:
    """
    Find all nodes upstream of a given node (dependency analysis).

    "What sources does this dashboard depend on?"
    """
    visited: set[str] = set()
    result: list[str] = []
    queue = deque(node.upstream)

    while queue:
        current = queue.popleft()
        if current.name in visited:
            continue
        visited.add(current.name)
        result.append(current.name)
        queue.extend(current.upstream)

    return result


def find_critical_path(
    node_map: dict[str, PipelineNode], target: str
) -> list[str]:
    """
    Find the longest path from any source to the target.

    The "critical path" determines the minimum execution time
    if all tasks take 1 unit of time.
    """
    target_node = node_map[target]

    def _longest_path(node: PipelineNode, visited: set[str]) -> list[str]:
        if not node.upstream:
            return [node.name]

        longest: list[str] = []
        for parent in node.upstream:
            if parent.name not in visited:
                visited.add(parent.name)
                path = _longest_path(parent, visited)
                visited.discard(parent.name)
                if len(path) > len(longest):
                    longest = path

        return longest + [node.name]

    return _longest_path(target_node, {target})


def compute_layers(node_map: dict[str, PipelineNode]) -> dict[str, int]:
    """
    Assign each node to a layer (execution order).

    Sources are layer 0. Each node's layer is 1 + max of its
    upstream layers. This determines parallel execution groups.
    """
    layers: dict[str, int] = {}

    def _get_layer(node: PipelineNode) -> int:
        if node.name in layers:
            return layers[node.name]

        if not node.upstream:
            layers[node.name] = 0
            return 0

        layer = 1 + max(_get_layer(parent) for parent in node.upstream)
        layers[node.name] = layer
        return layer

    for node in node_map.values():
        _get_layer(node)

    return layers


if __name__ == "__main__":
    nodes = [
        {"name": "raw_orders", "type": "source"},
        {"name": "raw_customers", "type": "source"},
        {"name": "raw_products", "type": "source"},
        {"name": "stg_orders", "type": "transform"},
        {"name": "stg_customers", "type": "transform"},
        {"name": "dim_customers", "type": "model"},
        {"name": "fct_orders", "type": "model"},
        {"name": "revenue_report", "type": "report"},
        {"name": "customer_dashboard", "type": "report"},
    ]

    edges = [
        ("raw_orders", "stg_orders"),
        ("raw_customers", "stg_customers"),
        ("raw_products", "fct_orders"),
        ("stg_orders", "fct_orders"),
        ("stg_customers", "dim_customers"),
        ("dim_customers", "fct_orders"),
        ("fct_orders", "revenue_report"),
        ("dim_customers", "customer_dashboard"),
        ("fct_orders", "customer_dashboard"),
    ]

    print("=== Pipeline DAG Analysis ===\n")

    dag = build_pipeline_dag(nodes, edges)

    print("  Impact analysis: if raw_orders changes, what's affected?")
    downstream = find_all_downstream(dag["raw_orders"])
    print(f"    {downstream}")

    print(f"\n  Dependency analysis: what does customer_dashboard need?")
    upstream = find_all_upstream(dag["customer_dashboard"])
    print(f"    {upstream}")

    print(f"\n  Critical path to revenue_report:")
    path = find_critical_path(dag, "revenue_report")
    print(f"    {' -> '.join(path)}")

    print(f"\n  Execution layers:")
    layers = compute_layers(dag)
    for layer_num in sorted(set(layers.values())):
        nodes_at_layer = [n for n, l in layers.items() if l == layer_num]
        print(f"    Layer {layer_num}: {nodes_at_layer}")
