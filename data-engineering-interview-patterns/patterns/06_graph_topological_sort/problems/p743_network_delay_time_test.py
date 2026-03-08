"""Tests for LeetCode 743: Network Delay Time."""

import pytest
from p743_network_delay_time import (
    network_delay_time,
    network_delay_time_bellman_ford,
)

APPROACHES = [network_delay_time, network_delay_time_bellman_ford]


class TestNetworkDelayTime:
    @pytest.mark.parametrize("fn", APPROACHES)
    def test_example(self, fn):
        assert fn([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2) == 2

    @pytest.mark.parametrize("fn", APPROACHES)
    def test_unreachable(self, fn):
        assert fn([[1, 2, 1]], 2, 2) == -1

    @pytest.mark.parametrize("fn", APPROACHES)
    def test_single_node(self, fn):
        assert fn([], 1, 1) == 0

    @pytest.mark.parametrize("fn", APPROACHES)
    def test_two_nodes(self, fn):
        assert fn([[1, 2, 5]], 2, 1) == 5

    @pytest.mark.parametrize("fn", APPROACHES)
    def test_multiple_paths(self, fn):
        """Should find shortest path, not first path."""
        times = [[1, 2, 10], [1, 3, 1], [3, 2, 1]]
        assert fn(times, 3, 1) == 2  # 1→3→2 is faster than 1→2

    @pytest.mark.parametrize("fn", APPROACHES)
    def test_diamond(self, fn):
        times = [[1, 2, 1], [1, 3, 4], [2, 3, 2]]
        assert fn(times, 3, 1) == 3  # 1→2 (1) then 1→2→3 (3) vs 1→3 (4)

    @pytest.mark.parametrize("fn", APPROACHES)
    def test_disconnected(self, fn):
        assert fn([[1, 2, 1]], 3, 1) == -1  # node 3 unreachable

    @pytest.mark.parametrize("fn", APPROACHES)
    def test_self_loop(self, fn):
        """Self-loop shouldn't affect result."""
        times = [[1, 1, 0], [1, 2, 3]]
        assert fn(times, 2, 1) == 3

    @pytest.mark.parametrize("fn", APPROACHES)
    def test_parallel_edges(self, fn):
        """Multiple edges between same nodes - should use shortest."""
        times = [[1, 2, 10], [1, 2, 1]]
        assert fn(times, 2, 1) == 1
