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
        return root  # p and q are in different subtrees -> root is LCA

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
