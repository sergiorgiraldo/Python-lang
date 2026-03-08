# CC Prompt: Create Pattern 10 Recursion/Trees (Part 4 of 5)

## What This Prompt Does

Creates problem 5: Serialize/Deserialize Binary Tree (LeetCode 297), plus DE scenarios 1-2: Org Chart Traversal and Category Tree Explosion.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

**Import convention:** `from tree_node import TreeNode, build_tree, tree_to_list`

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Every .md Worked Example starts with a prose paragraph
- Every approach explanation teaches the "why" not just the "what"

---

## Problem 5: Serialize and Deserialize Binary Tree (LeetCode #297)

### `problems/p297_serialize_deserialize.py`

```python
"""
LeetCode 297: Serialize and Deserialize Binary Tree

Pattern: Recursion - Tree to string and back
Difficulty: Hard
Time Complexity: O(n) for both serialize and deserialize
Space Complexity: O(n) for the serialized string and recursion
"""

from __future__ import annotations

from collections import deque
from typing import Optional

from tree_node import TreeNode


class Codec:
    """
    Serialize and deserialize a binary tree using pre-order traversal.

    Serialize: pre-order DFS, writing "null" for missing nodes.
    Deserialize: consume tokens in the same pre-order, building nodes.

    The pre-order traversal with null markers is unambiguous:
    it encodes both structure and values.
    """

    def serialize(self, root: Optional[TreeNode]) -> str:
        """Encode a tree to a comma-separated string."""
        tokens: list[str] = []
        self._serialize_helper(root, tokens)
        return ",".join(tokens)

    def _serialize_helper(
        self, node: Optional[TreeNode], tokens: list[str]
    ) -> None:
        if not node:
            tokens.append("null")
            return

        tokens.append(str(node.val))
        self._serialize_helper(node.left, tokens)
        self._serialize_helper(node.right, tokens)

    def deserialize(self, data: str) -> Optional[TreeNode]:
        """Decode a string back to a tree."""
        tokens = deque(data.split(","))
        return self._deserialize_helper(tokens)

    def _deserialize_helper(
        self, tokens: deque[str]
    ) -> Optional[TreeNode]:
        token = tokens.popleft()

        if token == "null":
            return None

        node = TreeNode(int(token))
        node.left = self._deserialize_helper(tokens)
        node.right = self._deserialize_helper(tokens)
        return node


class CodecBFS:
    """
    Alternative: BFS (level-order) serialization.

    Same format as LeetCode's tree representation.
    """

    def serialize(self, root: Optional[TreeNode]) -> str:
        if not root:
            return ""

        result: list[str] = []
        queue = deque([root])

        while queue:
            node = queue.popleft()
            if node:
                result.append(str(node.val))
                queue.append(node.left)
                queue.append(node.right)
            else:
                result.append("null")

        # Strip trailing nulls
        while result and result[-1] == "null":
            result.pop()

        return ",".join(result)

    def deserialize(self, data: str) -> Optional[TreeNode]:
        if not data:
            return None

        tokens = data.split(",")
        root = TreeNode(int(tokens[0]))
        queue = deque([root])
        i = 1

        while queue and i < len(tokens):
            node = queue.popleft()

            if i < len(tokens) and tokens[i] != "null":
                node.left = TreeNode(int(tokens[i]))
                queue.append(node.left)
            i += 1

            if i < len(tokens) and tokens[i] != "null":
                node.right = TreeNode(int(tokens[i]))
                queue.append(node.right)
            i += 1

        return root
```

### `problems/p297_serialize_deserialize_test.py`

```python
"""Tests for LeetCode 297: Serialize and Deserialize Binary Tree."""

import pytest

from tree_node import build_tree, tree_to_list
from .p297_serialize_deserialize import Codec, CodecBFS


@pytest.mark.parametrize("CodecClass", [Codec, CodecBFS])
class TestSerializeDeserialize:
    """Test both serialization approaches."""

    def test_roundtrip_basic(self, CodecClass) -> None:
        codec = CodecClass()
        root = build_tree([1, 2, 3, None, None, 4, 5])
        serialized = codec.serialize(root)
        restored = codec.deserialize(serialized)
        assert tree_to_list(restored) == tree_to_list(root)

    def test_roundtrip_empty(self, CodecClass) -> None:
        codec = CodecClass()
        serialized = codec.serialize(None)
        restored = codec.deserialize(serialized)
        assert restored is None

    def test_roundtrip_single(self, CodecClass) -> None:
        codec = CodecClass()
        root = build_tree([1])
        serialized = codec.serialize(root)
        restored = codec.deserialize(serialized)
        assert tree_to_list(restored) == [1]

    def test_roundtrip_left_skewed(self, CodecClass) -> None:
        codec = CodecClass()
        root = build_tree([1, 2, None, 3])
        serialized = codec.serialize(root)
        restored = codec.deserialize(serialized)
        assert tree_to_list(restored) == tree_to_list(root)

    def test_roundtrip_right_skewed(self, CodecClass) -> None:
        codec = CodecClass()
        root = build_tree([1, None, 2, None, 3])
        serialized = codec.serialize(root)
        restored = codec.deserialize(serialized)
        assert tree_to_list(restored) == tree_to_list(root)

    def test_roundtrip_balanced(self, CodecClass) -> None:
        codec = CodecClass()
        root = build_tree([1, 2, 3, 4, 5, 6, 7])
        serialized = codec.serialize(root)
        restored = codec.deserialize(serialized)
        assert tree_to_list(restored) == [1, 2, 3, 4, 5, 6, 7]

    def test_negative_values(self, CodecClass) -> None:
        codec = CodecClass()
        root = build_tree([-1, -2, -3])
        serialized = codec.serialize(root)
        restored = codec.deserialize(serialized)
        assert tree_to_list(restored) == [-1, -2, -3]

    def test_large_values(self, CodecClass) -> None:
        codec = CodecClass()
        root = build_tree([1000, 999, 1001])
        serialized = codec.serialize(root)
        restored = codec.deserialize(serialized)
        assert tree_to_list(restored) == [1000, 999, 1001]
```

### `problems/297_serialize_deserialize.md`

````markdown
# Serialize and Deserialize Binary Tree (LeetCode #297)

## Problem Statement

Design an algorithm to serialize a binary tree to a string and deserialize it back. There is no restriction on the format, but serialize and deserialize must be inverses of each other.

## Thought Process

1. **The challenge:** A tree is a 2D structure (nodes with pointers). A string is 1D. We need a serialization format that captures both values AND structure unambiguously.
2. **Pre-order with null markers:** If we serialize in pre-order (root, left, right) and write "null" for every missing child, the format is unambiguous. The decoder can reconstruct the exact tree by consuming tokens in the same order.
3. **Why pre-order?** The root comes first, which makes it natural to build the tree top-down during deserialization. Each recursive call consumes exactly the tokens for its subtree.

## Worked Example

Pre-order traversal with null markers creates an unambiguous encoding. The decoder reads tokens left to right, building nodes recursively. Each "null" token tells the decoder "this child doesn't exist, stop recursing on this side."

```
Tree:
      1
     / \
    2   3
       / \
      4   5

Serialize (pre-order with nulls):
  visit 1 → "1"
  visit 2 → "2"
    left of 2: null → "null"
    right of 2: null → "null"
  visit 3 → "3"
  visit 4 → "4"
    left of 4: null → "null"
    right of 4: null → "null"
  visit 5 → "5"
    left of 5: null → "null"
    right of 5: null → "null"

  Serialized: "1,2,null,null,3,4,null,null,5,null,null"

Deserialize:
  tokens: [1, 2, null, null, 3, 4, null, null, 5, null, null]

  consume "1" → create node(1)
    left: consume "2" → create node(2)
      left: consume "null" → return None
      right: consume "null" → return None
    right: consume "3" → create node(3)
      left: consume "4" → create node(4)
        left: consume "null" → return None
        right: consume "null" → return None
      right: consume "5" → create node(5)
        left: consume "null" → return None
        right: consume "null" → return None

  Each recursive call consumes exactly its own subtree's tokens.
  The deque (popleft) ensures tokens are consumed in order.
```

## Approaches

### Approach 1: Pre-order DFS

<details>
<summary>📝 Explanation</summary>

Serialize: walk the tree in pre-order. Append the node's value or "null" for missing nodes. Join with commas.

Deserialize: split the string on commas into a deque. Recursively consume tokens: if the token is "null", return None. Otherwise create a node and recursively build its left and right children.

The deque is critical: `popleft()` ensures each token is consumed exactly once and in the correct order. The recursion structure of deserialization mirrors the recursion structure of serialization, which guarantees they're inverses.

**Time:** O(n) for both serialize and deserialize. Each node produces/consumes exactly one token (plus two null markers for leaves).
**Space:** O(n) for the string. O(h) for the recursion stack.

</details>

### Approach 2: Level-order BFS

<details>
<summary>📝 Explanation</summary>

Serialize with BFS (level-order). This produces the same format LeetCode uses to display trees: `[1, 2, 3, null, null, 4, 5]`. Strip trailing nulls to save space.

Deserialize by processing tokens with a queue: create the root, then for each node in the queue, consume the next two tokens as its left and right children.

BFS serialization is more human-readable (it shows the tree level by level) and compact (trailing nulls stripped). DFS serialization is simpler to implement and reason about.

**Time:** O(n) for both.
**Space:** O(n) for the queue (up to n/2 nodes at the widest level).

</details>

## Edge Cases

| Input | Why It Matters |
|---|---|
| Empty tree | Serialize to empty string, deserialize back to None |
| Single node | Simplest non-empty tree |
| Left-skewed | Every node has only a left child |
| Negative values | "-1" must not be confused with a delimiter |
| Large values | Multi-digit numbers serialize correctly |

## Common Pitfalls

- **Not handling null markers:** Without explicit nulls, "1,2,3" is ambiguous (multiple tree structures produce the same in-order traversal).
- **Using a list index instead of a deque:** With a list you need to pass the index by reference (or use a mutable wrapper). A deque with popleft is cleaner.
- **Forgetting to handle the empty string in deserialize:** If serialize returns "" for None, deserialize must handle "" as input.

## Interview Tips

> "I'll use pre-order traversal with null markers. This captures both values and structure. Deserialization consumes tokens in the same order using a deque, recursively building the tree. Both operations are O(n)."

**This is a Hard problem.** Take time to explain the format before coding. Draw the serialized string and show how the decoder would consume it.

## DE Application

This bridges Pattern 09 (string parsing) and Pattern 10 (recursion). Serialization is everywhere in DE: JSON (tree → string), Avro/Parquet (nested structures → bytes), protocol buffers. Understanding how tree structures are serialized and restored helps debug data format issues and design efficient transport formats.

## Related Problems

- [449. Serialize and Deserialize BST](https://leetcode.com/problems/serialize-and-deserialize-bst/) - More efficient for BSTs
- [271. Encode and Decode Strings](https://leetcode.com/problems/encode-and-decode-strings/) - Pattern 09, same concept for flat lists
````

---

## DE Scenario 1: Org Chart Traversal

### `de_scenarios/org_chart.py`

```python
"""
DE Scenario: Org chart traversal using recursive processing.

Real-world application: reporting hierarchies, management chains,
headcount rollups. Shows the Python equivalent of SQL recursive CTEs.

Run: uv run python -m patterns.10_recursion_trees.de_scenarios.org_chart
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Employee:
    """An employee in an org chart."""

    id: int
    name: str
    title: str
    manager_id: int | None = None
    reports: list[Employee] = field(default_factory=list)


def build_org_tree(employees: list[dict]) -> Employee | None:
    """
    Build an org tree from a flat list of employee records.

    This is the Python equivalent of converting a parent-child table
    into a tree. In SQL, you'd use a recursive CTE. Here, we use
    a hash map (O(n)) to build parent-child links.
    """
    emp_map: dict[int, Employee] = {}

    # First pass: create all Employee objects
    for e in employees:
        emp_map[e["id"]] = Employee(
            id=e["id"],
            name=e["name"],
            title=e["title"],
            manager_id=e.get("manager_id"),
        )

    # Second pass: link children to parents
    root = None
    for emp in emp_map.values():
        if emp.manager_id is None:
            root = emp
        elif emp.manager_id in emp_map:
            emp_map[emp.manager_id].reports.append(emp)

    return root


def get_full_chain(root: Employee, target_id: int) -> list[str]:
    """
    Get the management chain from root to a specific employee.

    SQL equivalent: recursive CTE walking UP from the employee to the root.
    """

    def _find_path(node: Employee, target: int) -> list[str] | None:
        if node.id == target:
            return [node.name]

        for report in node.reports:
            path = _find_path(report, target)
            if path is not None:
                return [node.name] + path

        return None

    return _find_path(root, target_id) or []


def get_all_reports(employee: Employee) -> list[str]:
    """
    Get all direct and indirect reports (flattened).

    SQL equivalent: recursive CTE walking DOWN from a manager.
    """
    result: list[str] = []

    for report in employee.reports:
        result.append(report.name)
        result.extend(get_all_reports(report))

    return result


def headcount_rollup(employee: Employee) -> dict[str, int]:
    """
    Compute headcount rollup (each manager's total org size).

    For each manager: count = direct reports + all indirect reports.
    This is a post-order traversal: compute children's counts first,
    then sum for the parent.
    """

    def _count(emp: Employee) -> int:
        total = len(emp.reports)
        for report in emp.reports:
            total += _count(report)
        return total

    rollup: dict[str, int] = {}

    def _build_rollup(emp: Employee) -> None:
        rollup[emp.name] = _count(emp)
        for report in emp.reports:
            _build_rollup(report)

    _build_rollup(employee)
    return rollup


if __name__ == "__main__":
    employees = [
        {"id": 1, "name": "Alice", "title": "CEO", "manager_id": None},
        {"id": 2, "name": "Bob", "title": "VP Engineering", "manager_id": 1},
        {"id": 3, "name": "Charlie", "title": "VP Sales", "manager_id": 1},
        {"id": 4, "name": "Diana", "title": "Senior Engineer", "manager_id": 2},
        {"id": 5, "name": "Eve", "title": "Engineer", "manager_id": 2},
        {"id": 6, "name": "Frank", "title": "Sales Lead", "manager_id": 3},
        {"id": 7, "name": "Grace", "title": "Junior Engineer", "manager_id": 4},
    ]

    root = build_org_tree(employees)

    print("=== Org Chart Traversal ===\n")

    print("  Management chain to Grace:")
    chain = get_full_chain(root, 7)
    print(f"    {' → '.join(chain)}")

    print(f"\n  All reports under Bob:")
    reports = get_all_reports(root.reports[0])  # Bob
    print(f"    {reports}")

    print(f"\n  Headcount rollup:")
    rollup = headcount_rollup(root)
    for name, count in sorted(rollup.items(), key=lambda x: -x[1]):
        print(f"    {name}: {count}")
```

### `de_scenarios/org_chart.md`

````markdown
# DE Scenario: Org Chart Traversal

## Real-World Context

Every company has an org chart stored as a flat table: `(employee_id, name, title, manager_id)`. Turning this flat table into a tree and answering questions like "who reports to Bob, directly or indirectly?" or "what's the management chain from CEO to this engineer?" requires recursive traversal.

In SQL, this is a recursive CTE. In Python, it's the same tree traversal patterns from problems 104-297. Understanding both helps you choose the right tool and debug when queries behave unexpectedly.

## Worked Example

Build the tree from a flat list using a hash map (two passes: create nodes, then link them). Then traverse it recursively for different queries. Each query type maps to a different traversal pattern.

```
Flat data:
  (1, Alice, CEO, NULL)
  (2, Bob, VP Eng, 1)
  (3, Charlie, VP Sales, 1)
  (4, Diana, Sr Eng, 2)
  (5, Eve, Engineer, 2)
  (6, Frank, Sales Lead, 3)
  (7, Grace, Jr Eng, 4)

Tree:
  Alice (CEO)
  ├── Bob (VP Eng)
  │   ├── Diana (Sr Eng)
  │   │   └── Grace (Jr Eng)
  │   └── Eve (Engineer)
  └── Charlie (VP Sales)
      └── Frank (Sales Lead)

Queries:
  Management chain to Grace:
    Alice → Bob → Diana → Grace
    (DFS path finding, same as LCA path approach)

  All reports under Bob:
    [Diana, Grace, Eve]
    (DFS collecting all descendants)

  Headcount rollup:
    Alice: 6, Bob: 3, Charlie: 1, Diana: 1, Eve: 0, Frank: 0, Grace: 0
    (Post-order: compute children counts before parent)

SQL equivalent for "all reports under Bob":
  WITH RECURSIVE reports AS (
      SELECT id, name, manager_id FROM employees WHERE id = 2
      UNION ALL
      SELECT e.id, e.name, e.manager_id
      FROM employees e JOIN reports r ON e.manager_id = r.id
  )
  SELECT name FROM reports WHERE id != 2;
```
````

---

## DE Scenario 2: Category Tree Explosion

### `de_scenarios/category_tree.py`

```python
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
```

### `de_scenarios/category_tree.md`

````markdown
# DE Scenario: Category Tree Explosion

## Real-World Context

E-commerce category hierarchies are stored as flat tables (`id, name, parent_id`) but consumed as paths ("Electronics > Phones > Smartphones") for search indexing, breadcrumb navigation and dimension tables. "Exploding" the tree means generating every path from root to leaf.

## Worked Example

Build the tree from a flat list, then walk it recursively, accumulating the path string as you descend. Each node produces one record with its full path. Leaf nodes are flagged for filtering.

```
Flat data:
  (1, Electronics, NULL)
  (2, Phones, 1)
  (3, Laptops, 1)
  (4, Smartphones, 2)
  (5, Feature Phones, 2)
  (6, Gaming Laptops, 3)

Tree:
  Electronics
  ├── Phones
  │   ├── Smartphones
  │   └── Feature Phones
  └── Laptops
      └── Gaming Laptops

Explosion (all paths):
  Electronics
  Electronics > Phones
  Electronics > Phones > Smartphones
  Electronics > Phones > Feature Phones
  Electronics > Laptops
  Electronics > Laptops > Gaming Laptops

Dimension table output:
  id=1  depth=1  Electronics                            (not leaf)
  id=2  depth=2  Electronics > Phones                   (not leaf)
  id=4  depth=3  Electronics > Phones > Smartphones     (leaf)
  id=5  depth=3  Electronics > Phones > Feature Phones  (leaf)
  id=3  depth=2  Electronics > Laptops                  (not leaf)
  id=6  depth=3  Electronics > Laptops > Gaming Laptops (leaf)

SQL equivalent:
  WITH RECURSIVE cat_path AS (
      SELECT id, name, name AS full_path, 1 AS depth
      FROM categories WHERE parent_id IS NULL
      UNION ALL
      SELECT c.id, c.name, cp.full_path || ' > ' || c.name, cp.depth + 1
      FROM categories c JOIN cat_path cp ON c.parent_id = cp.id
  )
  SELECT * FROM cat_path;
```
````

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== Tests ==="
uv run pytest patterns/10_recursion_trees/problems/ -v --tb=short 2>&1 | tail -20

echo ""
echo "=== DE scenarios run ==="
uv run python -m patterns.10_recursion_trees.de_scenarios.org_chart 2>&1 | tail -10
echo ""
uv run python -m patterns.10_recursion_trees.de_scenarios.category_tree 2>&1 | tail -10
```
