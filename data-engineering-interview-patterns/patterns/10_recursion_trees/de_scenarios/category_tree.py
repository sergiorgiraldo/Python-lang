"""
DE Scenario: Category tree explosion for e-commerce.

Real-world application: building full category paths ("Electronics > Phones > Smartphones"),
computing category-level metrics, and flattening hierarchies for search indexes.

Run: uv run python -m patterns.10_recursion_trees.de_scenarios.category_tree
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Category:
    """A category in a product hierarchy."""

    id: int
    name: str
    parent_id: int | None = None
    children: list[Category] = field(default_factory=list)


def build_category_tree(categories: list[dict]) -> list[Category]:
    """Build forest of category trees from flat records."""
    cat_map: dict[int, Category] = {}

    for c in categories:
        cat_map[c["id"]] = Category(
            id=c["id"],
            name=c["name"],
            parent_id=c.get("parent_id"),
        )

    roots: list[Category] = []
    for cat in cat_map.values():
        if cat.parent_id is None:
            roots.append(cat)
        elif cat.parent_id in cat_map:
            cat_map[cat.parent_id].children.append(cat)

    return roots


def get_full_paths(roots: list[Category]) -> list[str]:
    """
    Generate full category paths for every leaf and intermediate node.

    "Electronics > Phones > Smartphones"

    This is the "explosion" - turning a tree into a flat list of paths.
    Essential for search indexing and breadcrumb navigation.
    """
    paths: list[str] = []

    def _walk(node: Category, prefix: str) -> None:
        current_path = f"{prefix} > {node.name}" if prefix else node.name
        paths.append(current_path)

        for child in node.children:
            _walk(child, current_path)

    for root in roots:
        _walk(root, "")

    return paths


def compute_depth(node: Category) -> int:
    """Compute the depth of a category subtree."""
    if not node.children:
        return 1
    return 1 + max(compute_depth(child) for child in node.children)


def flatten_to_records(
    roots: list[Category],
) -> list[dict]:
    """
    Flatten the tree into records with full path and depth.

    Output format suitable for loading into a dimension table.
    """
    records: list[dict] = []

    def _flatten(node: Category, path: str, depth: int) -> None:
        current_path = f"{path} > {node.name}" if path else node.name
        is_leaf = len(node.children) == 0

        records.append({
            "id": node.id,
            "name": node.name,
            "full_path": current_path,
            "depth": depth,
            "is_leaf": is_leaf,
        })

        for child in node.children:
            _flatten(child, current_path, depth + 1)

    for root in roots:
        _flatten(root, "", 1)

    return records


if __name__ == "__main__":
    categories = [
        {"id": 1, "name": "Electronics", "parent_id": None},
        {"id": 2, "name": "Phones", "parent_id": 1},
        {"id": 3, "name": "Laptops", "parent_id": 1},
        {"id": 4, "name": "Smartphones", "parent_id": 2},
        {"id": 5, "name": "Feature Phones", "parent_id": 2},
        {"id": 6, "name": "Gaming Laptops", "parent_id": 3},
        {"id": 7, "name": "Clothing", "parent_id": None},
        {"id": 8, "name": "Shirts", "parent_id": 7},
        {"id": 9, "name": "T-Shirts", "parent_id": 8},
    ]

    print("=== Category Tree Explosion ===\n")

    roots = build_category_tree(categories)

    print("  Full paths:")
    for path in get_full_paths(roots):
        print(f"    {path}")

    print(f"\n  Flattened dimension table:")
    for record in flatten_to_records(roots):
        leaf = " (leaf)" if record["is_leaf"] else ""
        print(f"    depth={record['depth']} {record['full_path']}{leaf}")
