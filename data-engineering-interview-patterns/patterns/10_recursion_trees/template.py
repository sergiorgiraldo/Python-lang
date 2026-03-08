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
