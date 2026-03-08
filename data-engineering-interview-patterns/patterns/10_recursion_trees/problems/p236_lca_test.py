"""Tests for LeetCode 236: Lowest Common Ancestor."""

import pytest

from tree_node import build_tree
from p236_lca import lowest_common_ancestor, lca_with_path


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
