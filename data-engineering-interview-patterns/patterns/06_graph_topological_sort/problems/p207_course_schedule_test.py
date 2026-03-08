"""Tests for LeetCode 207: Course Schedule."""

import pytest
from p207_course_schedule import can_finish_dfs, can_finish_kahn


class TestCanFinish:
    @pytest.mark.parametrize("fn", [can_finish_kahn, can_finish_dfs])
    def test_no_prereqs(self, fn):
        assert fn(2, []) is True

    @pytest.mark.parametrize("fn", [can_finish_kahn, can_finish_dfs])
    def test_simple_chain(self, fn):
        assert fn(2, [[1, 0]]) is True

    @pytest.mark.parametrize("fn", [can_finish_kahn, can_finish_dfs])
    def test_simple_cycle(self, fn):
        assert fn(2, [[1, 0], [0, 1]]) is False

    @pytest.mark.parametrize("fn", [can_finish_kahn, can_finish_dfs])
    def test_diamond(self, fn):
        """Diamond shape: 0→1→3, 0→2→3. No cycle."""
        assert fn(4, [[1, 0], [2, 0], [3, 1], [3, 2]]) is True

    @pytest.mark.parametrize("fn", [can_finish_kahn, can_finish_dfs])
    def test_three_node_cycle(self, fn):
        assert fn(3, [[1, 0], [2, 1], [0, 2]]) is False

    @pytest.mark.parametrize("fn", [can_finish_kahn, can_finish_dfs])
    def test_disconnected(self, fn):
        """Disconnected components, no cycle."""
        assert fn(4, [[1, 0], [3, 2]]) is True

    @pytest.mark.parametrize("fn", [can_finish_kahn, can_finish_dfs])
    def test_single_course(self, fn):
        assert fn(1, []) is True

    @pytest.mark.parametrize("fn", [can_finish_kahn, can_finish_dfs])
    def test_self_loop(self, fn):
        assert fn(1, [[0, 0]]) is False

    @pytest.mark.parametrize("fn", [can_finish_kahn, can_finish_dfs])
    def test_long_chain(self, fn):
        """0→1→2→3→4. No cycle."""
        edges = [[i + 1, i] for i in range(4)]
        assert fn(5, edges) is True

    @pytest.mark.parametrize("fn", [can_finish_kahn, can_finish_dfs])
    def test_cycle_in_subgraph(self, fn):
        """Node 0 is fine, but 1→2→3→1 is a cycle."""
        assert fn(4, [[1, 0], [2, 1], [3, 2], [1, 3]]) is False
