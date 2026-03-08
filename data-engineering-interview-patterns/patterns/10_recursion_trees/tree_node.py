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
