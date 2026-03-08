# CC Prompt: Create Pattern 10 Recursion/Trees (Part 1 of 5)

## What This Prompt Does

Creates the foundation for pattern 10: directory structure, shared TreeNode class, template.py, conftest.py and a deep-teaching README.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- Create all files as specified. If files already exist, REPLACE them.
- NO Oxford commas, NO em dashes, NO exclamation points
- Python code: typed, documented, clean

---

## Directory Setup

```
patterns/10_recursion_trees/
├── README.md
├── __init__.py
├── template.py
├── tree_node.py              ← shared TreeNode class + helpers
├── problems/
│   ├── __init__.py
│   └── conftest.py
└── de_scenarios/
    └── __init__.py
```

Create any missing directories and `__init__.py` files.

## Create `problems/conftest.py`

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))
```

Note: the second path insert allows `from tree_node import TreeNode` from test files.

## Create `tree_node.py`

This is the shared TreeNode class used by ALL problems in this pattern.

```python
"""
Shared TreeNode class for binary tree problems.

Includes helper functions for building trees from lists (LeetCode format)
and converting trees back to lists for test assertions.
"""

from __future__ import annotations

from collections import deque
from typing import Optional


class TreeNode:
    """Binary tree node."""

    def __init__(
        self,
        val: int = 0,
        left: Optional[TreeNode] = None,
        right: Optional[TreeNode] = None,
    ):
        self.val = val
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"TreeNode({self.val})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TreeNode):
            return NotImplemented
        return (
            self.val == other.val
            and self.left == other.left
            and self.right == other.right
        )


def build_tree(values: list[Optional[int]]) -> Optional[TreeNode]:
    """
    Build a binary tree from a level-order list (LeetCode format).

    [3, 9, 20, None, None, 15, 7] builds:
          3
         / \\
        9   20
           / \\
          15   7

    None values represent missing nodes.
    """
    if not values or values[0] is None:
        return None

    root = TreeNode(values[0])
    queue = deque([root])
    i = 1

    while queue and i < len(values):
        node = queue.popleft()

        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1

        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1

    return root


def tree_to_list(root: Optional[TreeNode]) -> list[Optional[int]]:
    """
    Convert a binary tree to level-order list (LeetCode format).

    Inverse of build_tree. Trailing Nones are stripped.
    """
    if not root:
        return []

    result: list[Optional[int]] = []
    queue = deque([root])

    while queue:
        node = queue.popleft()
        if node:
            result.append(node.val)
            queue.append(node.left)
            queue.append(node.right)
        else:
            result.append(None)

    # Strip trailing Nones
    while result and result[-1] is None:
        result.pop()

    return result
```

## Create `template.py`

```python
"""
Recursion and Tree Pattern Template

Three common approaches for tree problems:

1. RECURSIVE DFS: process node, recurse on children
2. ITERATIVE DFS: explicit stack replaces call stack
3. BFS (LEVEL ORDER): queue-based, process level by level
"""

from __future__ import annotations

from collections import deque
from typing import Optional

from .tree_node import TreeNode


def dfs_recursive_template(root: Optional[TreeNode]) -> int:
    """
    Template: recursive DFS.

    Base case: empty node returns a default value.
    Recursive case: combine results from left and right subtrees.

    This pattern solves: max depth, tree sum, path problems.
    """
    if not root:
        return 0  # base case

    left_result = dfs_recursive_template(root.left)
    right_result = dfs_recursive_template(root.right)

    return 1 + max(left_result, right_result)  # combine


def dfs_iterative_template(root: Optional[TreeNode]) -> list[int]:
    """
    Template: iterative DFS using an explicit stack.

    Equivalent to recursive DFS but avoids stack overflow
    for very deep trees.
    """
    if not root:
        return []

    result: list[int] = []
    stack = [root]

    while stack:
        node = stack.pop()
        result.append(node.val)

        # Push right first so left is processed first (LIFO)
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)

    return result


def bfs_template(root: Optional[TreeNode]) -> list[list[int]]:
    """
    Template: BFS level-order traversal.

    Process all nodes at depth d before any node at depth d+1.
    Uses a queue. Returns values grouped by level.
    """
    if not root:
        return []

    result: list[list[int]] = []
    queue = deque([root])

    while queue:
        level_size = len(queue)
        level: list[int] = []

        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.val)

            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

        result.append(level)

    return result
```

## Replace `README.md`

```markdown
# Recursion and Tree Patterns

## What Is It?

### The basics

A binary tree is a hierarchical data structure where each node has at most two children (left and right). Trees are recursive by nature: every subtree is itself a tree. This makes recursion the natural tool for tree problems.

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
```

That's the entire data structure. Three fields. The complexity comes from how you traverse and process it.

### Why recursion works for trees

Every tree problem follows the same recursive structure:
1. **Base case:** What do you return for an empty node (None)?
2. **Recursive case:** Process the current node, recurse on left and right children, combine the results.

```python
def solve(node):
    if not node:
        return base_value          # base case

    left = solve(node.left)        # recurse left
    right = solve(node.right)      # recurse right

    return combine(node, left, right)  # combine
```

The "combine" step is what changes between problems. For max depth, it's `1 + max(left, right)`. For tree sum, it's `node.val + left + right`. For "is this a valid BST?", it's a range check. But the structure is always the same.

### Three traversal orders

How you order the "process current node" step relative to the recursive calls determines the traversal:

```
        1
       / \
      2   3
     / \
    4   5

Pre-order  (process, left, right): 1, 2, 4, 5, 3
In-order   (left, process, right): 4, 2, 5, 1, 3
Post-order (left, right, process): 4, 5, 2, 3, 1
Level-order (BFS):                 1, 2, 3, 4, 5
```

**Pre-order** visits the root first. Useful for copying trees or prefix expressions.
**In-order** visits nodes in sorted order for BSTs. Useful for validation and sorted output.
**Post-order** visits children before parent. Useful when you need child results before processing the parent (e.g., computing heights).
**Level-order (BFS)** visits by depth. Useful for shortest path and level-based processing.

### Recursion vs iteration

Every recursive solution can be converted to an iterative one using an explicit stack. The recursive call stack and the explicit stack hold the same information. Recursion is usually cleaner for trees, but iteration avoids stack overflow for very deep trees (Python's default recursion limit is 1000).

```python
# Recursive
def preorder(node):
    if not node:
        return []
    return [node.val] + preorder(node.left) + preorder(node.right)

# Iterative (same result)
def preorder_iterative(root):
    result, stack = [], [root]
    while stack:
        node = stack.pop()
        if node:
            result.append(node.val)
            stack.append(node.right)  # right first (LIFO)
            stack.append(node.left)
    return result
```

### Connection to data engineering

Trees and recursion appear throughout DE work:

- **Hierarchical data:** Org charts, category trees, geographic hierarchies (country → state → city). SQL handles these with recursive CTEs.
- **Query execution plans:** Database query plans are trees. Understanding tree traversal helps you read and optimize execution plans.
- **DAG traversal:** Pipeline DAGs are trees (or more precisely, directed acyclic graphs). Topological sort (Pattern 06) is tree traversal generalized to graphs.
- **Nested JSON/XML:** Document structures are trees. Parsing and flattening them is tree traversal.
- **Bill of materials:** Manufacturing and dependency trees that need "explosion" (expanding all nested components) use recursive processing.

The recursive CTE in SQL (`WITH RECURSIVE`) is the direct SQL equivalent of recursive tree traversal in Python. Understanding one makes the other intuitive.

### What the problems in this section cover

| Problem | Concept | What it teaches |
|---|---|---|
| Max Depth | Base case + combine | The simplest tree recursion |
| Invert Binary Tree | Recursive transformation | Modifying tree structure |
| Subtree of Another Tree | Tree comparison | Combining traversal with matching |
| Lowest Common Ancestor | Path-based reasoning | Finding shared structure |
| Serialize/Deserialize | Tree ↔ string | Bridges recursion and parsing |

## When to Use It

**Recognition signals in interviews:**
- The input is a TreeNode or hierarchical structure
- "Find the depth/height/diameter..."
- "Check if this tree is valid/balanced/symmetric..."
- "Find the path between two nodes..."
- "Flatten or serialize a tree..."

**Recognition signals in DE work:**
- Hierarchical data that needs traversal or flattening
- Recursive CTEs in SQL
- Pipeline dependency analysis
- Nested document processing

## Visual Aid

```
Tree structure and recursive depth calculation:

        3
       / \
      9   20
         / \
        15   7

  maxDepth(3):
    left  = maxDepth(9)  = 1  (leaf: base + 1)
    right = maxDepth(20) = 2
      left  = maxDepth(15) = 1
      right = maxDepth(7)  = 1
      return 1 + max(1, 1) = 2
    return 1 + max(1, 2) = 3

  Each recursive call handles a smaller subtree.
  The base case (None → 0) stops the recursion.
  Results bubble up from leaves to root.
```

## Trade-offs

**Recursion vs iteration:**
- Recursion: cleaner code, natural fit for trees. Risk of stack overflow for deep trees (Python limit ~1000).
- Iteration with stack: avoids overflow, can be faster (no function call overhead). More verbose.
- For interviews, use recursion unless the problem specifically requires handling very deep trees.

**DFS vs BFS:**
- DFS (depth-first): uses O(h) space where h is height. Better for deep, narrow trees.
- BFS (breadth-first): uses O(w) space where w is max width. Better for wide, shallow trees.
- DFS finds depth/path answers naturally. BFS finds level-order and shortest-path answers naturally.

## Problems in This Section

| # | Problem | Difficulty | Key Concept |
|---|---|---|---|
| 104 | [Maximum Depth](problems/104_max_depth.md) | Easy | Base case + recursive combine |
| 226 | [Invert Binary Tree](problems/226_invert_tree.md) | Easy | Recursive transformation |
| 572 | [Subtree of Another Tree](problems/572_subtree.md) | Easy | Tree comparison with DFS |
| 236 | [Lowest Common Ancestor](problems/236_lca.md) | Medium | Path finding in trees |
| 297 | [Serialize/Deserialize](problems/297_serialize_deserialize.md) | Hard | Tree ↔ string conversion |

## DE Scenarios

| Scenario | Technique | Real-World Use |
|---|---|---|
| [Org Chart Traversal](de_scenarios/org_chart.md) | Recursive CTE | Reporting hierarchies |
| [Category Tree Explosion](de_scenarios/category_tree.md) | Recursive expansion | E-commerce category paths |
| [Bill of Materials](de_scenarios/bill_of_materials.md) | Recursive explosion | Manufacturing dependencies |
| [Pipeline DAG Analysis](de_scenarios/pipeline_dag.md) | Graph traversal | Upstream/downstream discovery |
```

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== Files created ==="
find patterns/10_recursion_trees/ -type f | sort

echo ""
echo "=== README subsections ==="
grep "^### " patterns/10_recursion_trees/README.md

echo ""
echo "=== Key teaching sections ==="
for section in "The basics" "recursion works" "traversal orders" "Recursion vs iteration" "Connection to data" "Visual Aid" "Trade-offs"; do
    grep -qi "$section" patterns/10_recursion_trees/README.md && echo "✅ $section" || echo "❌ $section"
done

echo ""
echo "=== TreeNode imports work ==="
uv run python -c "
from patterns.recursion_trees_10.tree_node import TreeNode, build_tree, tree_to_list
t = build_tree([3, 9, 20, None, None, 15, 7])
print(f'Root: {t}, to_list: {tree_to_list(t)}')
" 2>&1 || echo "Import path may need adjustment - CC should fix"

# Alternative import path if the above fails
uv run python -c "
import sys; sys.path.insert(0, 'patterns/10_recursion_trees')
from tree_node import TreeNode, build_tree, tree_to_list
t = build_tree([3, 9, 20, None, None, 15, 7])
print(f'Root: {t}, to_list: {tree_to_list(t)}')
"
```
