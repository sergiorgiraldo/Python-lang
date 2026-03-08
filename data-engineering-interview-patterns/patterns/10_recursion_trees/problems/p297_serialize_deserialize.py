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
