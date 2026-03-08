"""Tests for LeetCode 104: Maximum Depth of Binary Tree."""

import pytest

from tree_node import build_tree
from p104_max_depth import max_depth, max_depth_iterative


@pytest.mark.parametrize("func", [max_depth, max_depth_iterative])
class TestMaxDepth:
    """Test both implementations."""

    def test_example(self, func) -> None:
        root = build_tree([3, 9, 20, None, None, 15, 7])
        assert func(root) == 3

    def test_single_node(self, func) -> None:
        root = build_tree([1])
        assert func(root) == 1

    def test_empty_tree(self, func) -> None:
        assert func(None) == 0

    def test_left_skewed(self, func) -> None:
        root = build_tree([1, 2, None, 3, None, 4])
        assert func(root) == 4

    def test_right_skewed(self, func) -> None:
        root = build_tree([1, None, 2, None, 3])
        assert func(root) == 3

    def test_balanced(self, func) -> None:
        root = build_tree([1, 2, 3, 4, 5, 6, 7])
        assert func(root) == 3

    def test_two_nodes_left(self, func) -> None:
        root = build_tree([1, 2])
        assert func(root) == 2

    def test_two_nodes_right(self, func) -> None:
        root = build_tree([1, None, 2])
        assert func(root) == 2
