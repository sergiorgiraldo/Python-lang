# CC Prompt: Create Pattern 10 Recursion/Trees (Part 3 of 5)

## What This Prompt Does

Creates problems 3-4: Subtree of Another Tree (LeetCode 572) and Lowest Common Ancestor (LeetCode 236).

Work in `~/dev/projects/data-engineering-interview-patterns/`.

**Import convention:** Solution files use `from tree_node import TreeNode, build_tree`. Test files use `from tree_node import TreeNode, build_tree, tree_to_list`. The conftest.py in Part 1 adds the parent directory to sys.path so this import works.

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Every .md Worked Example starts with a prose paragraph
- Every approach explanation teaches the "why" not just the "what"

---

## Problem 3: Subtree of Another Tree (LeetCode #572)

### `problems/p572_subtree.py`

```python
"""
LeetCode 572: Subtree of Another Tree

Pattern: Recursion - Tree comparison
Difficulty: Easy
Time Complexity: O(m * n) where m = nodes in root, n = nodes in subRoot
Space Complexity: O(h) for recursion stack
"""

from __future__ import annotations

from typing import Optional

from tree_node import TreeNode


def is_subtree(root: Optional[TreeNode], sub_root: Optional[TreeNode]) -> bool:
    """
    Check if subRoot is a subtree of root.

    A subtree means there exists a node in root such that the
    subtree rooted at that node is identical to subRoot.

    Two-step approach:
    1. Traverse root to find nodes matching subRoot's root value.
    2. At each match, check if the entire subtrees are identical.
    """
    if not sub_root:
        return True  # empty tree is a subtree of anything
    if not root:
        return False  # non-empty sub can't be subtree of empty tree

    if _is_same_tree(root, sub_root):
        return True

    return is_subtree(root.left, sub_root) or is_subtree(root.right, sub_root)


def _is_same_tree(p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:
    """Check if two trees are identical."""
    if not p and not q:
        return True
    if not p or not q:
        return False
    return (
        p.val == q.val
        and _is_same_tree(p.left, q.left)
        and _is_same_tree(p.right, q.right)
    )
```

### `problems/p572_subtree_test.py`

```python
"""Tests for LeetCode 572: Subtree of Another Tree."""

import pytest

from tree_node import build_tree
from .p572_subtree import is_subtree


class TestSubtree:
    """Core subtree tests."""

    def test_is_subtree(self) -> None:
        root = build_tree([3, 4, 5, 1, 2])
        sub = build_tree([4, 1, 2])
        assert is_subtree(root, sub) is True

    def test_not_subtree(self) -> None:
        root = build_tree([3, 4, 5, 1, 2, None, None, None, None, 0])
        sub = build_tree([4, 1, 2])
        assert is_subtree(root, sub) is False

    def test_identical_trees(self) -> None:
        root = build_tree([1, 2, 3])
        sub = build_tree([1, 2, 3])
        assert is_subtree(root, sub) is True

    def test_empty_subtree(self) -> None:
        root = build_tree([1, 2, 3])
        assert is_subtree(root, None) is True

    def test_empty_root(self) -> None:
        sub = build_tree([1])
        assert is_subtree(None, sub) is False

    def test_both_empty(self) -> None:
        assert is_subtree(None, None) is True

    def test_single_node_match(self) -> None:
        root = build_tree([1, 2, 3])
        sub = build_tree([2])
        assert is_subtree(root, sub) is True

    def test_single_node_no_match(self) -> None:
        root = build_tree([1, 2, 3])
        sub = build_tree([4])
        assert is_subtree(root, sub) is False

    def test_leaf_subtree(self) -> None:
        root = build_tree([1, 2, 3, 4])
        sub = build_tree([4])
        assert is_subtree(root, sub) is True
```

### `problems/572_subtree.md`

````markdown
# Subtree of Another Tree (LeetCode #572)

## Problem Statement

Given the roots of two binary trees `root` and `subRoot`, return True if there is a subtree of `root` with the same structure and node values as `subRoot`.

## Thought Process

1. **Two separate recursive checks:** First, traverse `root` looking for nodes where the subtree might start. Second, at each candidate node, check if the subtrees are identical.
2. **"Same tree" helper:** Comparing two trees for equality is itself recursive: same value at the root, same left subtree, same right subtree.
3. **Combine:** For each node in `root`, check "is the tree rooted here identical to `subRoot`?" If yes at any node, return True.

## Worked Example

Two levels of recursion: the outer one traverses the main tree looking for a match, the inner one compares entire subtrees node by node. The outer traversal visits every node in `root`. At each node, the inner comparison runs against `subRoot`.

```
root:            subRoot:
    3               4
   / \             / \
  4   5           1   2
 / \
1   2

Outer traversal of root:
  Node 3: is tree(3) same as tree(4)?
    3 vs 4 → values differ. No.
  Recurse left → Node 4: is tree(4) same as tree(4)?
    4 vs 4 → match. Check children:
      1 vs 1 → match. Children: None vs None → match (both leaves).
      2 vs 2 → match. Children: None vs None → match.
    All nodes match. → TRUE.

  Return True (found at node 4).

Worst case: every node in root triggers a full comparison
with subRoot. O(m * n) where m = |root|, n = |subRoot|.
```

## Approaches

### Approach 1: DFS + Same Tree Check

<details>
<summary>📝 Explanation</summary>

Two functions: `is_subtree` traverses the main tree, calling `is_same_tree` at each node. `is_same_tree` does a node-by-node comparison of two trees.

`is_subtree(root, sub)`:
- If sub is None, return True (empty tree is a subtree of anything).
- If root is None, return False (non-empty sub can't match empty root).
- If `is_same_tree(root, sub)`, return True.
- Otherwise, recurse: `is_subtree(root.left, sub) or is_subtree(root.right, sub)`.

`is_same_tree(p, q)`:
- If both None, return True.
- If one is None or values differ, return False.
- Recurse on both children.

**Time:** O(m * n) worst case. For each of m nodes in root, we might compare n nodes in subRoot. In practice, most comparisons fail early at the root value check.
**Space:** O(h) for the recursion stack where h is the height of root.

There are O(m + n) approaches using tree serialization or hashing, but the recursive approach is cleaner for interviews and sufficient for all but extreme cases.

</details>

## Edge Cases

| Input | Expected | Why |
|---|---|---|
| `subRoot` is None | True | Empty tree is always a subtree |
| `root` is None, `subRoot` is not | False | Can't find a non-empty subtree in nothing |
| Identical trees | True | The whole tree is a subtree of itself |
| Same values but different structure | False | Structure must match exactly |

## Common Pitfalls

- **Confusing "subtree" with "substructure":** A subtree must match from a node all the way down to the leaves. A node in root with the same value but extra children below doesn't count.
- **Forgetting the None-None base case in is_same_tree:** Both None is True (matching empty subtrees), not False.

## Interview Tips

> "I'll use two recursive functions: one to traverse the main tree finding candidate roots, and one to compare entire subtrees. The comparison function checks value equality and recurses on both children."

## DE Application

Schema comparison: checking if a subset schema exists within a larger document structure. Also used in AST (abstract syntax tree) matching for code analysis tools and query plan comparison in query optimization.

## Related Problems

- [100. Same Tree](https://leetcode.com/problems/same-tree/) - The helper function on its own
- [652. Find Duplicate Subtrees](https://leetcode.com/problems/find-duplicate-subtrees/) - Find all matching subtrees
````

---

## Problem 4: Lowest Common Ancestor (LeetCode #236)

### `problems/p236_lca.py`

```python
"""
LeetCode 236: Lowest Common Ancestor of a Binary Tree

Pattern: Recursion - Path finding
Difficulty: Medium
Time Complexity: O(n)
Space Complexity: O(h)
"""

from __future__ import annotations

from typing import Optional

from tree_node import TreeNode


def lowest_common_ancestor(
    root: Optional[TreeNode], p: TreeNode, q: TreeNode
) -> Optional[TreeNode]:
    """
    Find the lowest common ancestor (LCA) of two nodes.

    The LCA is the deepest node that has both p and q as descendants
    (a node can be a descendant of itself).

    Recursive insight: if the current node is p or q, it's a potential
    LCA. If p and q are found in different subtrees, the current node
    IS the LCA. If both are in the same subtree, the LCA is deeper
    in that subtree.
    """
    if not root or root == p or root == q:
        return root

    left = lowest_common_ancestor(root.left, p, q)
    right = lowest_common_ancestor(root.right, p, q)

    if left and right:
        return root  # p and q are in different subtrees → root is LCA

    return left if left else right


def lca_with_path(
    root: Optional[TreeNode], p: TreeNode, q: TreeNode
) -> Optional[TreeNode]:
    """
    Alternative: find paths to both nodes, then find where paths diverge.

    More intuitive but uses O(n) extra space for the paths.
    """
    path_p = _find_path(root, p)
    path_q = _find_path(root, q)

    if not path_p or not path_q:
        return None

    lca = None
    for a, b in zip(path_p, path_q):
        if a == b:
            lca = a
        else:
            break

    return lca


def _find_path(
    root: Optional[TreeNode], target: TreeNode
) -> list[TreeNode]:
    """Find the path from root to target. Returns empty list if not found."""
    if not root:
        return []
    if root == target:
        return [root]

    left_path = _find_path(root.left, target)
    if left_path:
        return [root] + left_path

    right_path = _find_path(root.right, target)
    if right_path:
        return [root] + right_path

    return []
```

### `problems/p236_lca_test.py`

```python
"""Tests for LeetCode 236: Lowest Common Ancestor."""

import pytest

from tree_node import build_tree
from .p236_lca import lowest_common_ancestor, lca_with_path


class TestLCA:
    """Test the main recursive approach."""

    def _find_node(self, root, val):
        """Helper to find a node by value for test setup."""
        if not root:
            return None
        if root.val == val:
            return root
        return self._find_node(root.left, val) or self._find_node(root.right, val)

    def test_example_1(self) -> None:
        root = build_tree([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
        p = self._find_node(root, 5)
        q = self._find_node(root, 1)
        assert lowest_common_ancestor(root, p, q).val == 3

    def test_example_2(self) -> None:
        root = build_tree([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
        p = self._find_node(root, 5)
        q = self._find_node(root, 4)
        assert lowest_common_ancestor(root, p, q).val == 5

    def test_ancestor_is_self(self) -> None:
        root = build_tree([1, 2])
        p = root
        q = self._find_node(root, 2)
        assert lowest_common_ancestor(root, p, q).val == 1

    def test_same_node(self) -> None:
        root = build_tree([1, 2, 3])
        p = self._find_node(root, 2)
        assert lowest_common_ancestor(root, p, p).val == 2

    def test_siblings(self) -> None:
        root = build_tree([1, 2, 3])
        p = self._find_node(root, 2)
        q = self._find_node(root, 3)
        assert lowest_common_ancestor(root, p, q).val == 1

    def test_deep_nodes(self) -> None:
        root = build_tree([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
        p = self._find_node(root, 7)
        q = self._find_node(root, 4)
        assert lowest_common_ancestor(root, p, q).val == 2


class TestLCAWithPath:
    """Test the path-based approach."""

    def _find_node(self, root, val):
        if not root:
            return None
        if root.val == val:
            return root
        return self._find_node(root.left, val) or self._find_node(root.right, val)

    def test_example_1(self) -> None:
        root = build_tree([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
        p = self._find_node(root, 5)
        q = self._find_node(root, 1)
        assert lca_with_path(root, p, q).val == 3

    def test_example_2(self) -> None:
        root = build_tree([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
        p = self._find_node(root, 5)
        q = self._find_node(root, 4)
        assert lca_with_path(root, p, q).val == 5
```

### `problems/236_lca.md`

````markdown
# Lowest Common Ancestor (LeetCode #236)

## Problem Statement

Given a binary tree and two nodes p and q, find their lowest common ancestor (LCA). The LCA is the deepest node that has both p and q as descendants (a node can be a descendant of itself).

## Thought Process

1. **What does LCA mean?** The deepest node that is an ancestor of both p and q. If p is an ancestor of q, then p itself is the LCA.
2. **Recursive insight:** From any node, p and q can be in one of three configurations: both in the left subtree, both in the right subtree, or split across the two subtrees. If they're split, the current node is the LCA.
3. **How to detect:** Recurse on both children. If both return non-None, the current node is the LCA (p and q are in different subtrees). If only one returns non-None, both are in that subtree and the deeper result is the LCA.

## Worked Example

The recursion returns the first node where p and q are found in different subtrees. If a node IS p or q, it returns itself immediately (acting as both a "found" signal and a potential LCA). The "both children return non-None" case is the split detection.

```
        3
       / \
      5   1
     / \ / \
    6  2 0  8
      / \
     7   4

Find LCA of p=5 and q=4:

  lca(3):
    left = lca(5):
      root == p (5). Return 5. ← found p
    right = lca(1):
      left = lca(0): no p or q. Return None.
      right = lca(8): no p or q. Return None.
      Both None → return None. ← q not in right subtree of 3

  Wait, q=4 is in the LEFT subtree (under 5). Let me retrace:

  lca(3):
    left = lca(5):
      root == p. Return 5 immediately.
      (Doesn't recurse further - this is the key optimization)
    right = lca(1):
      Returns None (q=4 not here).
    Only left returned non-None → return left = node 5.

  Answer: 5. Node 5 is ancestor of both itself and node 4.

  The early return at p=5 works because: if p is an ancestor of q,
  then p IS the LCA. We don't need to find q separately.

Find LCA of p=5 and q=1:

  lca(3):
    left = lca(5): returns 5 (found p).
    right = lca(1): returns 1 (found q).
    Both non-None → current node (3) is the LCA.

  Answer: 3. p and q are in different subtrees of 3.
```

## Approaches

### Approach 1: Recursive (One-Pass)

<details>
<summary>📝 Explanation</summary>

The recursion does three things at each node:
1. If the node is None, return None (base case: not found).
2. If the node is p or q, return the node (found one of them).
3. Recurse on both children. If both return non-None, the current node is the LCA (split case). If only one returns non-None, return that result (both p and q are in that subtree).

The elegance: the function returns the "first relevant node" it finds in each subtree. When both subtrees return something, the current node must be the LCA because the two targets are split across its children.

**Time:** O(n) - visit each node at most once.
**Space:** O(h) - recursion depth equals tree height.

This is the standard solution. It's O(n) with a single traversal and doesn't require storing paths.

</details>

### Approach 2: Find Paths, Then Compare

<details>
<summary>📝 Explanation</summary>

Find the path from root to p and from root to q. The LCA is the last node that appears in both paths before they diverge.

More intuitive but requires two traversals and O(n) extra space for the paths. The path-finding itself is a useful subroutine (e.g., "print the path between two nodes in a tree").

**Time:** O(n) - two traversals.
**Space:** O(n) - storing two paths.

Useful when you actually need the paths (not just the LCA). Otherwise the one-pass recursive approach is cleaner.

</details>

## Edge Cases

| Input | Expected | Why |
|---|---|---|
| p is ancestor of q | p | A node is its own descendant |
| p == q | p | Same node, LCA is itself |
| p and q are siblings | Parent | Simplest split case |
| p and q are at max depth | Their first common ancestor | May be far up the tree |

## Common Pitfalls

- **Forgetting "a node can be a descendant of itself":** If p is the ancestor of q, the LCA is p, not p's parent.
- **Searching for values instead of node references:** The problem gives you node references (p, q), not values. Compare with `==` (identity), not by value.

## Interview Tips

> "I'll use a recursive approach. At each node, I recurse left and right. If both return non-None, the current node is the LCA because p and q are in different subtrees. If one returns None, the LCA is in the other subtree."

**Common follow-up:** "What if this were a BST?" → Use the BST property: if both values are less than root, go left. If both greater, go right. If they split, root is the LCA. O(h) instead of O(n).

## DE Application

Finding the common root of two columns in a schema hierarchy. "What's the closest common ancestor table for these two derived metrics?" In an org chart, finding the closest shared manager between two employees. In a data lineage graph, finding where two data products share a common source.

## Related Problems

- [235. LCA of a BST](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-search-tree/) - Simpler with BST property
- [1644. LCA of a Binary Tree II](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree-ii/) - When p or q might not exist
````

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== Tests ==="
uv run pytest patterns/10_recursion_trees/problems/ -v --tb=short 2>&1 | tail -20

echo ""
echo "=== Worked Examples ==="
for f in patterns/10_recursion_trees/problems/572_subtree.md patterns/10_recursion_trees/problems/236_lca.md; do
    first=$(awk '/^## Worked Example/{found=1; next} found && /\S/{print; exit}' "$f")
    echo "$(basename $f): $first" | head -c 80
    echo ""
done
```
