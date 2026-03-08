# CC Prompt: Create Pattern 10 Recursion/Trees (Part 2 of 5)

## What This Prompt Does

Creates problems 1-2: Maximum Depth of Binary Tree (LeetCode 104) and Invert Binary Tree (LeetCode 226).

Work in `~/dev/projects/data-engineering-interview-patterns/`.

**Important:** All tree problems import TreeNode from `tree_node.py` (created in Part 1). Use `from tree_node import TreeNode, build_tree, tree_to_list` in solution files and tests. Adjust the import path as needed so tests pass with `uv run pytest`.

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Every .md Worked Example starts with a prose paragraph
- Every approach explanation teaches the "why" not just the "what"

---

## Problem 1: Maximum Depth of Binary Tree (LeetCode #104)

### `problems/p104_max_depth.py`

```python
"""
LeetCode 104: Maximum Depth of Binary Tree

Pattern: Recursion - Base case + recursive combine
Difficulty: Easy
Time Complexity: O(n) - visit every node
Space Complexity: O(h) - recursion stack depth equals tree height
"""

from __future__ import annotations

from collections import deque
from typing import Optional

from tree_node import TreeNode


def max_depth(root: Optional[TreeNode]) -> int:
    """
    Return the maximum depth of a binary tree.

    Depth = number of nodes along the longest path from root to leaf.

    Recursive approach: the depth of a tree is 1 (for the root) plus
    the maximum depth of its left and right subtrees. An empty tree
    has depth 0.
    """
    if not root:
        return 0

    return 1 + max(max_depth(root.left), max_depth(root.right))


def max_depth_iterative(root: Optional[TreeNode]) -> int:
    """
    Iterative BFS approach. Count the number of levels.

    Each level adds 1 to the depth. Process level by level
    using a queue.
    """
    if not root:
        return 0

    depth = 0
    queue = deque([root])

    while queue:
        depth += 1
        for _ in range(len(queue)):
            node = queue.popleft()
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

    return depth
```

### `problems/p104_max_depth_test.py`

```python
"""Tests for LeetCode 104: Maximum Depth of Binary Tree."""

import pytest

from tree_node import build_tree
from .p104_max_depth import max_depth, max_depth_iterative


@pytest.mark.parametrize("func", [max_depth, max_depth_iterative])
class TestMaxDepth:
    """Test both implementations."""

    def test_example(self, func) -> None:
        root = build_tree([3, 9, 20, None, None, 15, 7])
        assert func(root) == 3

    def test_single_node(self, func) -> None:
        root = build_tree([1])
        assert func(root) == 1

    def test_empty_tree(self, func) -> None:
        assert func(None) == 0

    def test_left_skewed(self, func) -> None:
        root = build_tree([1, 2, None, 3, None, 4])
        assert func(root) == 4

    def test_right_skewed(self, func) -> None:
        root = build_tree([1, None, 2, None, 3])
        assert func(root) == 3

    def test_balanced(self, func) -> None:
        root = build_tree([1, 2, 3, 4, 5, 6, 7])
        assert func(root) == 3

    def test_two_nodes_left(self, func) -> None:
        root = build_tree([1, 2])
        assert func(root) == 2

    def test_two_nodes_right(self, func) -> None:
        root = build_tree([1, None, 2])
        assert func(root) == 2
```

### `problems/104_max_depth.md`

````markdown
# Maximum Depth of Binary Tree (LeetCode #104)

## Problem Statement

Given the root of a binary tree, return its maximum depth. Maximum depth is the number of nodes along the longest path from root to the farthest leaf.

## Thought Process

1. **Base case:** An empty tree (None) has depth 0.
2. **Recursive case:** The depth of a tree is 1 (the current node) plus the maximum of its left subtree's depth and right subtree's depth.
3. **That's it.** This is the simplest tree recursion and the foundation for every other tree problem.

## Worked Example

Every tree problem starts with the same question: what's the base case, and how do I combine child results? For max depth, the base case is "empty tree → 0" and the combination is "1 + max(left depth, right depth)." The recursion handles all the traversal automatically.

```
        3
       / \
      9   20
         / \
        15   7

  maxDepth(3):
    maxDepth(9):
      maxDepth(None) = 0     ← base case
      maxDepth(None) = 0     ← base case
      return 1 + max(0, 0) = 1
    maxDepth(20):
      maxDepth(15):
        return 1 + max(0, 0) = 1
      maxDepth(7):
        return 1 + max(0, 0) = 1
      return 1 + max(1, 1) = 2
    return 1 + max(1, 2) = 3

  Answer: 3 (path: 3 → 20 → 15 or 3 → 20 → 7)

  The recursion visits every node exactly once: O(n).
  The call stack depth equals the tree height: O(h).
  For a balanced tree, h = log(n). For a skewed tree, h = n.
```

## Approaches

### Approach 1: Recursive DFS

<details>
<summary>📝 Explanation</summary>

The classic recursive solution. If the node is None, return 0. Otherwise return 1 plus the max of the recursive calls on left and right children.

This is post-order traversal: we need the child results (depths) before we can compute the parent's depth. The recursion handles this naturally because the recursive calls complete before the current call returns.

**Time:** O(n) - every node is visited exactly once.
**Space:** O(h) where h is the tree height. The recursion stack holds one frame per level. For a balanced tree, h = O(log n). For a completely skewed tree (linked list), h = O(n).

This is the textbook starting point for tree problems. Master this pattern and every other tree problem is a variation.

</details>

### Approach 2: Iterative BFS

<details>
<summary>📝 Explanation</summary>

Use a queue to process the tree level by level. Each level adds 1 to the depth counter. The number of levels IS the max depth.

Process all nodes at the current level (using the queue's current size), enqueue their children, increment the depth counter. When the queue is empty, all levels have been processed.

**Time:** O(n) - same as recursive.
**Space:** O(w) where w is the maximum width of the tree. For a balanced tree, the bottom level has ~n/2 nodes, so space is O(n). For a skewed tree, each level has 1 node, so space is O(1).

BFS is a natural fit when you're counting levels. DFS is more natural when you're computing path-based properties.

</details>

## Edge Cases

| Input | Expected | Why |
|---|---|---|
| `None` | 0 | Empty tree |
| `[1]` | 1 | Single node is both root and leaf |
| `[1, 2, None, 3, None, 4]` | 4 | Left-skewed (worst case for recursion depth) |
| `[1, 2, 3, 4, 5, 6, 7]` | 3 | Balanced tree |

## Common Pitfalls

- **Confusing depth with height:** Some definitions count edges (height) vs nodes (depth). LeetCode counts nodes. Clarify in the interview.
- **Forgetting the +1:** `max(left, right)` gives the subtree depth. You need `1 + max(left, right)` to include the current node.

## Interview Tips

> "The depth of a tree is 1 plus the max depth of its subtrees. Base case: an empty tree has depth 0. This visits every node once, so it's O(n) time and O(h) space for the recursion stack."

This is often a warm-up problem. Solve it quickly and cleanly to build momentum.

## DE Application

Measuring hierarchy depth in data. "How many levels deep is our org chart?" is the same computation. In SQL: `WITH RECURSIVE` to walk the hierarchy, counting levels. The recursive CTE's anchor clause is the base case, and the recursive clause is the "1 + recurse on children" step.

## Related Problems

- [111. Minimum Depth](https://leetcode.com/problems/minimum-depth-of-binary-tree/) - Similar but finds the shallowest leaf
- [543. Diameter of Binary Tree](https://leetcode.com/problems/diameter-of-binary-tree/) - Max depth variant tracking the longest path through any node
````

---

## Problem 2: Invert Binary Tree (LeetCode #226)

### `problems/p226_invert_tree.py`

```python
"""
LeetCode 226: Invert Binary Tree

Pattern: Recursion - Recursive transformation
Difficulty: Easy
Time Complexity: O(n) - visit every node
Space Complexity: O(h) - recursion stack depth
"""

from __future__ import annotations

from collections import deque
from typing import Optional

from tree_node import TreeNode


def invert_tree(root: Optional[TreeNode]) -> Optional[TreeNode]:
    """
    Invert a binary tree (mirror it).

    Every left child becomes the right child and vice versa,
    recursively through the entire tree.
    """
    if not root:
        return None

    root.left, root.right = root.right, root.left
    invert_tree(root.left)
    invert_tree(root.right)

    return root


def invert_tree_iterative(root: Optional[TreeNode]) -> Optional[TreeNode]:
    """Iterative BFS approach: swap children at each level."""
    if not root:
        return None

    queue = deque([root])

    while queue:
        node = queue.popleft()
        node.left, node.right = node.right, node.left

        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)

    return root
```

### `problems/p226_invert_tree_test.py`

```python
"""Tests for LeetCode 226: Invert Binary Tree."""

import pytest

from tree_node import build_tree, tree_to_list
from .p226_invert_tree import invert_tree, invert_tree_iterative


class TestInvertTree:
    """Test recursive approach."""

    def test_example(self) -> None:
        root = build_tree([4, 2, 7, 1, 3, 6, 9])
        result = invert_tree(root)
        assert tree_to_list(result) == [4, 7, 2, 9, 6, 3, 1]

    def test_empty(self) -> None:
        assert invert_tree(None) is None

    def test_single_node(self) -> None:
        root = build_tree([1])
        result = invert_tree(root)
        assert tree_to_list(result) == [1]

    def test_two_levels(self) -> None:
        root = build_tree([2, 1, 3])
        result = invert_tree(root)
        assert tree_to_list(result) == [2, 3, 1]

    def test_left_only(self) -> None:
        root = build_tree([1, 2])
        result = invert_tree(root)
        assert tree_to_list(result) == [1, None, 2]

    def test_right_only(self) -> None:
        root = build_tree([1, None, 2])
        result = invert_tree(root)
        assert tree_to_list(result) == [1, 2]


class TestInvertTreeIterative:
    """Test iterative approach (needs fresh tree each time)."""

    def test_example(self) -> None:
        root = build_tree([4, 2, 7, 1, 3, 6, 9])
        result = invert_tree_iterative(root)
        assert tree_to_list(result) == [4, 7, 2, 9, 6, 3, 1]

    def test_empty(self) -> None:
        assert invert_tree_iterative(None) is None

    def test_single_node(self) -> None:
        root = build_tree([1])
        result = invert_tree_iterative(root)
        assert tree_to_list(result) == [1]

    def test_two_levels(self) -> None:
        root = build_tree([2, 1, 3])
        result = invert_tree_iterative(root)
        assert tree_to_list(result) == [2, 3, 1]
```

### `problems/226_invert_tree.md`

````markdown
# Invert Binary Tree (LeetCode #226)

## Problem Statement

Given the root of a binary tree, invert the tree and return its root. Inverting means swapping every left and right child throughout the tree.

```
Input:       Output:
    4            4
   / \          / \
  2   7   →   7   2
 / \ / \     / \ / \
1  3 6  9   9  6 3  1
```

## Thought Process

1. **What does "invert" mean?** At every node, swap its left and right children. Do this recursively and the whole tree mirrors.
2. **Base case:** An empty node (None) stays None.
3. **Recursive case:** Swap current node's children, then recursively invert both subtrees.
4. **Order doesn't matter:** You can swap before or after recursing. Pre-order or post-order both work. The swap at each node is independent.

## Worked Example

At each node, swap left and right pointers. The recursion ensures this happens at every level. The key insight: swapping at the root alone only mirrors the top level. Recursing ensures every level gets mirrored.

```
Input tree:
        4
       / \
      2   7
     / \ / \
    1  3 6  9

Step 1: At node 4, swap children.
        4
       / \
      7   2       ← 7 and 2 swapped
     / \ / \
    6  9 1  3     ← but subtrees came along unchanged

Step 2: Recurse on node 7 (was right, now left). Swap its children.
        4
       / \
      7   2
     / \ / \
    9  6 1  3     ← 9 and 6 swapped within the 7 subtree

Step 3: Recurse on node 2 (was left, now right). Swap its children.
        4
       / \
      7   2
     / \ / \
    9  6 3  1     ← 3 and 1 swapped within the 2 subtree

Result: [4, 7, 2, 9, 6, 3, 1]

Each node visited once. O(n) time, O(h) space.
```

## Approaches

### Approach 1: Recursive DFS

<details>
<summary>📝 Explanation</summary>

At each node, swap `node.left` and `node.right` using Python's tuple swap. Then recurse on both children. The base case (None) returns None.

Python's tuple swap `root.left, root.right = root.right, root.left` is atomic - both sides are evaluated before assignment, so no temp variable is needed.

The recursion order (pre-order: swap then recurse, vs post-order: recurse then swap) doesn't affect correctness. Both visit every node and perform the swap.

**Time:** O(n) - visit every node once.
**Space:** O(h) - recursion depth equals tree height.

Three lines of code after the base case. This is recursion at its cleanest.

</details>

### Approach 2: Iterative BFS

<details>
<summary>📝 Explanation</summary>

Use a queue to process nodes level by level. For each node, swap its children and enqueue them. The queue ensures every node gets processed.

Functionally identical to the recursive version but uses an explicit queue instead of the call stack. Useful if the tree could be extremely deep (avoiding stack overflow) or if you prefer iterative solutions.

**Time:** O(n).
**Space:** O(w) where w is the max width (up to n/2 for a balanced tree).

</details>

## Edge Cases

| Input | Expected | Why |
|---|---|---|
| `None` | `None` | Empty tree stays empty |
| `[1]` | `[1]` | Single node is its own mirror |
| `[1, 2]` | `[1, None, 2]` | Left child becomes right child |
| `[1, 2, 3, 4, 5, 6, 7]` | `[1, 3, 2, 7, 6, 5, 4]` | Full balanced tree |

## Common Pitfalls

- **Modifying the tree in place vs returning a new tree:** This problem modifies in place. If the problem asked for a new tree, you'd create new nodes.
- **Swapping only at the root:** The swap must happen at every node, not just the top.

## Interview Tips

> "Invert means swap left and right at every node, recursively. Base case: None stays None. At each node: swap children, recurse on both. O(n) time since we visit every node once."

This is often a quick warm-up. Demonstrate clean recursion and move on.

## DE Application

Data transformation patterns. Mirroring a tree structure is analogous to pivoting or transposing hierarchical data. More practically, the pattern of "apply a transformation at every node" is the same pattern used when transforming nested JSON documents (changing keys, restructuring levels).

## Related Problems

- [101. Symmetric Tree](https://leetcode.com/problems/symmetric-tree/) - Check if a tree is its own mirror
- [100. Same Tree](https://leetcode.com/problems/same-tree/) - Compare two trees node by node
````

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== Tests ==="
uv run pytest patterns/10_recursion_trees/problems/ -v --tb=short 2>&1 | tail -20

echo ""
echo "=== Worked Examples start with prose ==="
for f in patterns/10_recursion_trees/problems/104_max_depth.md patterns/10_recursion_trees/problems/226_invert_tree.md; do
    first=$(awk '/^## Worked Example/{found=1; next} found && /\S/{print; exit}' "$f")
    echo "$(basename $f): $first" | head -c 80
    echo ""
done
```
