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
