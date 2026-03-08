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
