"""Tests for LeetCode 226: Invert Binary Tree."""

import pytest

from tree_node import build_tree, tree_to_list
from p226_invert_tree import invert_tree, invert_tree_iterative


class TestInvertTree:
    """Test recursive approach."""

    def test_example(self) -> None:
        root = build_tree([4, 2, 7, 1, 3, 6, 9])
        result = invert_tree(root)
        assert tree_to_list(result) == [4, 7, 2, 9, 6, 3, 1]

    def test_empty(self) -> None:
        assert invert_tree(None) is None

    def test_single_node(self) -> None:
        root = build_tree([1])
        result = invert_tree(root)
        assert tree_to_list(result) == [1]

    def test_two_levels(self) -> None:
        root = build_tree([2, 1, 3])
        result = invert_tree(root)
        assert tree_to_list(result) == [2, 3, 1]

    def test_left_only(self) -> None:
        root = build_tree([1, 2])
        result = invert_tree(root)
        assert tree_to_list(result) == [1, None, 2]

    def test_right_only(self) -> None:
        root = build_tree([1, None, 2])
        result = invert_tree(root)
        assert tree_to_list(result) == [1, 2]


class TestInvertTreeIterative:
    """Test iterative approach (needs fresh tree each time)."""

    def test_example(self) -> None:
        root = build_tree([4, 2, 7, 1, 3, 6, 9])
        result = invert_tree_iterative(root)
        assert tree_to_list(result) == [4, 7, 2, 9, 6, 3, 1]

    def test_empty(self) -> None:
        assert invert_tree_iterative(None) is None

    def test_single_node(self) -> None:
        root = build_tree([1])
        result = invert_tree_iterative(root)
        assert tree_to_list(result) == [1]

    def test_two_levels(self) -> None:
        root = build_tree([2, 1, 3])
        result = invert_tree_iterative(root)
        assert tree_to_list(result) == [2, 3, 1]
