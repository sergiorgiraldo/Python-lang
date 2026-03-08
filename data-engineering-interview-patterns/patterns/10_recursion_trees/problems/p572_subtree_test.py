"""Tests for LeetCode 572: Subtree of Another Tree."""

import pytest

from tree_node import build_tree
from p572_subtree import is_subtree


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
