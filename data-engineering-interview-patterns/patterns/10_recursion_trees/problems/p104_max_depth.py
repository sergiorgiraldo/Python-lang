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
