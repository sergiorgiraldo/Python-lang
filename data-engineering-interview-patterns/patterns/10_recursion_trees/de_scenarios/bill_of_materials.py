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

    # Search from all root components
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
