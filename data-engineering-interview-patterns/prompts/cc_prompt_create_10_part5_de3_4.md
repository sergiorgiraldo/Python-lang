# CC Prompt: Create Pattern 10 Recursion/Trees (Part 5 of 5)

## What This Prompt Does

Creates DE scenarios 3-4: Bill of Materials and Pipeline DAG Analysis.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Every .md Worked Example starts with a prose paragraph
- DE scenarios include both .py (runnable with demo) and .md (documented)

---

## DE Scenario 3: Bill of Materials

### `de_scenarios/bill_of_materials.py`

```python
"""
DE Scenario: Bill of materials (BOM) explosion.

Real-world application: manufacturing systems need to expand a finished
product into all its component parts (recursively), computing total
quantities needed. Also applies to recipe ingredients, software
dependencies and cost rollups.

Run: uv run python -m patterns.10_recursion_trees.de_scenarios.bill_of_materials
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Component:
    """A component in a bill of materials."""

    id: str
    name: str
    unit_cost: float
    quantity: float = 1.0  # quantity needed per parent unit
    children: list[Component] = field(default_factory=list)


def build_bom_tree(
    components: list[dict], relationships: list[dict]
) -> dict[str, Component]:
    """
    Build BOM trees from component and relationship lists.

    Returns a map of component_id to Component with children linked.
    """
    comp_map: dict[str, Component] = {}

    for c in components:
        comp_map[c["id"]] = Component(
            id=c["id"],
            name=c["name"],
            unit_cost=c["unit_cost"],
        )

    for rel in relationships:
        parent = comp_map[rel["parent_id"]]
        child_template = comp_map[rel["child_id"]]
        child = Component(
            id=child_template.id,
            name=child_template.name,
            unit_cost=child_template.unit_cost,
            quantity=rel["quantity"],
            children=child_template.children,
        )
        parent.children.append(child)

    return comp_map


def explode_bom(component: Component, parent_qty: float = 1.0) -> list[dict]:
    """
    Explode a BOM: list all components with total quantities.

    For each child, total_quantity = parent_quantity * child_quantity_per_parent.
    This multiplies down through all levels.

    A bicycle needs 2 wheels. Each wheel needs 32 spokes.
    Total spokes for one bicycle: 1 * 2 * 32 = 64.
    """
    result: list[dict] = []
    effective_qty = parent_qty * component.quantity

    result.append({
        "id": component.id,
        "name": component.name,
        "quantity_per_unit": component.quantity,
        "total_quantity": effective_qty,
        "unit_cost": component.unit_cost,
        "total_cost": effective_qty * component.unit_cost,
    })

    for child in component.children:
        result.extend(explode_bom(child, effective_qty))

    return result


def total_cost(component: Component, quantity: float = 1.0) -> float:
    """
    Compute the total cost of a component including all sub-components.

    Post-order traversal: compute children costs first, then add own cost.
    """
    cost = component.unit_cost * quantity

    for child in component.children:
        child_qty = quantity * child.quantity
        cost += total_cost(child, child_qty)

    return cost


def find_where_used(
    comp_map: dict[str, Component], target_id: str
) -> list[list[str]]:
    """
    Find all assemblies that use a given component (reverse lookup).

    "Where is this part used?" - traces upward through all paths.
    """
    paths: list[list[str]] = []

    def _search(node: Component, current_path: list[str]) -> None:
        current_path = current_path + [node.name]

        if node.id == target_id:
            paths.append(current_path)
            return

        for child in node.children:
            _search(child, current_path)

    for comp in comp_map.values():
        if comp.children and not any(
            r["parent_id"] == comp.id
            for r in []  # would need relationships list
        ):
            pass

    # Simpler: search from all root components
    roots = [c for c in comp_map.values() if all(
        c.id not in [child.id for child in other.children]
        for other in comp_map.values()
    )]

    for root in roots:
        _search(root, [])

    return paths


if __name__ == "__main__":
    components = [
        {"id": "BIKE", "name": "Bicycle", "unit_cost": 0},
        {"id": "FRAME", "name": "Frame", "unit_cost": 85.00},
        {"id": "WHEEL", "name": "Wheel Assembly", "unit_cost": 5.00},
        {"id": "TIRE", "name": "Tire", "unit_cost": 12.50},
        {"id": "SPOKE", "name": "Spoke", "unit_cost": 0.25},
        {"id": "HUB", "name": "Hub", "unit_cost": 8.00},
        {"id": "CHAIN", "name": "Chain", "unit_cost": 15.00},
        {"id": "PEDAL", "name": "Pedal", "unit_cost": 7.50},
    ]

    relationships = [
        {"parent_id": "BIKE", "child_id": "FRAME", "quantity": 1},
        {"parent_id": "BIKE", "child_id": "WHEEL", "quantity": 2},
        {"parent_id": "BIKE", "child_id": "CHAIN", "quantity": 1},
        {"parent_id": "BIKE", "child_id": "PEDAL", "quantity": 2},
        {"parent_id": "WHEEL", "child_id": "TIRE", "quantity": 1},
        {"parent_id": "WHEEL", "child_id": "SPOKE", "quantity": 32},
        {"parent_id": "WHEEL", "child_id": "HUB", "quantity": 1},
    ]

    print("=== Bill of Materials Explosion ===\n")

    comp_map = build_bom_tree(components, relationships)
    bike = comp_map["BIKE"]

    print("  BOM for one Bicycle:")
    for item in explode_bom(bike):
        indent = "    "
        print(f"{indent}{item['name']:20s} qty={item['total_quantity']:6.0f}  "
              f"cost=${item['total_cost']:8.2f}")

    print(f"\n  Total cost per bicycle: ${total_cost(bike):.2f}")
```

### `de_scenarios/bill_of_materials.md`

````markdown
# DE Scenario: Bill of Materials Explosion

## Real-World Context

Manufacturing, retail and software systems maintain bills of materials (BOMs): a product is made of components, which are made of sub-components, recursively. "Exploding" a BOM means flattening this tree into a list of all parts with their total quantities and costs.

The same pattern applies to recipe systems (ingredients of sub-recipes), software dependency trees (package A depends on B which depends on C) and cost allocation hierarchies.

## Worked Example

BOM explosion multiplies quantities down through the tree. A bicycle needs 2 wheels. Each wheel needs 32 spokes. Total spokes per bicycle: 2 x 32 = 64. The recursion carries the parent's quantity into each child, multiplying at each level.

```
Bicycle (qty: 1)
├── Frame (qty: 1)              → 1 x 1 = 1 frame
├── Wheel Assembly (qty: 2)     → 1 x 2 = 2 assemblies
│   ├── Tire (qty: 1)           → 2 x 1 = 2 tires
│   ├── Spoke (qty: 32)         → 2 x 32 = 64 spokes
│   └── Hub (qty: 1)            → 2 x 1 = 2 hubs
├── Chain (qty: 1)              → 1 x 1 = 1 chain
└── Pedal (qty: 2)              → 1 x 2 = 2 pedals

Cost rollup (post-order traversal):
  Spoke:  64 x $0.25 = $16.00
  Hub:    2 x $8.00  = $16.00
  Tire:   2 x $12.50 = $25.00
  Wheel:  2 x $5.00  = $10.00 (assembly cost)
  Wheel total:         $67.00 (assembly + sub-components)
  Frame:  1 x $85.00 = $85.00
  Chain:  1 x $15.00 = $15.00
  Pedal:  2 x $7.50  = $15.00
  Bicycle total:       $182.00

SQL equivalent:
  WITH RECURSIVE bom AS (
      SELECT child_id, quantity, quantity AS total_qty
      FROM relationships WHERE parent_id = 'BIKE'
      UNION ALL
      SELECT r.child_id, r.quantity, bom.total_qty * r.quantity
      FROM relationships r JOIN bom ON r.parent_id = bom.child_id
  )
  SELECT c.name, bom.total_qty, bom.total_qty * c.unit_cost AS total_cost
  FROM bom JOIN components c ON bom.child_id = c.id;
```

## Key Design Decisions

1. **Quantity multiplication is the core operation.** Each level multiplies the parent's effective quantity by the child's per-unit quantity. This is where mistakes happen.
2. **Assembly cost vs component cost.** A wheel assembly has its own cost ($5 for labor) plus the cost of its sub-components. The rollup must add both.
3. **Shared components.** A spoke might appear in both front and rear wheel assemblies. The explosion lists it twice (once per parent). Aggregation (GROUP BY component) gives the total across the entire product.
````

---

## DE Scenario 4: Pipeline DAG Analysis

### `de_scenarios/pipeline_dag.py`

```python
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
    print(f"    {' → '.join(path)}")

    print(f"\n  Execution layers:")
    layers = compute_layers(dag)
    for layer_num in sorted(set(layers.values())):
        nodes_at_layer = [n for n, l in layers.items() if l == layer_num]
        print(f"    Layer {layer_num}: {nodes_at_layer}")
```

### `de_scenarios/pipeline_dag.md`

````markdown
# DE Scenario: Pipeline DAG Analysis

## Real-World Context

Every data platform is a directed acyclic graph (DAG): sources feed transforms, transforms feed models, models feed reports. Answering "what's affected if this source breaks?" (downstream/impact analysis) and "what does this dashboard depend on?" (upstream/dependency analysis) requires graph traversal.

Tools like dbt, Airflow and Dagster build these DAGs. Understanding the traversal mechanics helps you debug lineage issues and design efficient execution strategies.

## Worked Example

A pipeline DAG extends tree traversal to handle multiple parents (a model can depend on several transforms). BFS with a visited set handles the fan-in correctly, avoiding duplicate processing when two paths converge on the same node.

```
Pipeline:
  raw_orders ──→ stg_orders ──→ fct_orders ──→ revenue_report
  raw_customers → stg_customers → dim_customers ─┬→ customer_dashboard
  raw_products ──────────────────→ fct_orders ───┘

Impact analysis: raw_orders changes
  BFS from raw_orders:
    → stg_orders
    → fct_orders (via stg_orders)
    → revenue_report (via fct_orders)
    → customer_dashboard (via fct_orders)
  Result: [stg_orders, fct_orders, revenue_report, customer_dashboard]

Dependency analysis: customer_dashboard
  BFS upstream from customer_dashboard:
    → dim_customers, fct_orders
    → stg_customers (via dim_customers)
    → stg_orders, raw_products, dim_customers (via fct_orders)
       (dim_customers already visited, skip)
    → raw_customers (via stg_customers)
    → raw_orders (via stg_orders)
  Result: all upstream nodes

Execution layers (what can run in parallel):
  Layer 0: raw_orders, raw_customers, raw_products (sources, no deps)
  Layer 1: stg_orders, stg_customers (depend only on layer 0)
  Layer 2: dim_customers (depends on layer 1)
  Layer 3: fct_orders (depends on layers 0, 1, 2)
  Layer 4: revenue_report, customer_dashboard (depend on layer 3)
```

## Key Design Decisions

1. **BFS with visited set.** Unlike trees, DAGs have multiple paths to the same node. Without a visited set, you'd process nodes multiple times.
2. **Separate upstream and downstream links.** Store both directions so you can traverse in either direction without rebuilding the graph.
3. **Layer computation for parallelism.** A node's layer is 1 + max of its upstream layers. Nodes in the same layer can execute in parallel.
````

---

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== DE Scenario files ==="
ls patterns/10_recursion_trees/de_scenarios/*.py patterns/10_recursion_trees/de_scenarios/*.md 2>/dev/null

echo ""
echo "=== Run DE scenarios ==="
uv run python -m patterns.10_recursion_trees.de_scenarios.org_chart 2>&1 | tail -8
echo ""
uv run python -m patterns.10_recursion_trees.de_scenarios.category_tree 2>&1 | tail -8
echo ""
uv run python -m patterns.10_recursion_trees.de_scenarios.bill_of_materials 2>&1 | tail -8
echo ""
uv run python -m patterns.10_recursion_trees.de_scenarios.pipeline_dag 2>&1 | tail -8

echo ""
echo "=== Full Pattern 10 test suite ==="
uv run pytest patterns/10_recursion_trees/ -v --tb=short 2>&1 | tail -20

echo ""
echo "=== Pattern 10 completeness ==="
echo "Problems:"
ls patterns/10_recursion_trees/problems/*.md 2>/dev/null | wc -l
echo "(should be 5)"
echo "DE Scenarios:"
ls patterns/10_recursion_trees/de_scenarios/*.md 2>/dev/null | wc -l
echo "(should be 4)"
echo "Worked Examples:"
grep -rl "## Worked Example" patterns/10_recursion_trees/ | wc -l
echo "(should be 9: 5 problems + 4 DE scenarios)"

echo ""
echo "=== Style check ==="
grep -r "—" patterns/10_recursion_trees/ && echo "❌ Em dashes found" || echo "✅ No em dashes"
grep -rn "## Visual Walkthrough" patterns/10_recursion_trees/ && echo "❌ Wrong section name" || echo "✅ Correct section names"
```
