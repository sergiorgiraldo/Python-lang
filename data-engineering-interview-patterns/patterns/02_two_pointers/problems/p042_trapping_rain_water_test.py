"""Tests for LeetCode 42: Trapping Rain Water."""

import pytest
from p042_trapping_rain_water import trap, trap_prefix_max


class TestTrap:
    """Test the two-pointer solution."""

    def test_basic(self):
        assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

    def test_v_shape(self):
        assert trap([4, 2, 0, 3, 2, 5]) == 9

    def test_simple_pool(self):
        assert trap([1, 0, 1]) == 1

    def test_empty(self):
        assert trap([]) == 0

    def test_single(self):
        assert trap([5]) == 0

    def test_two_bars(self):
        assert trap([3, 5]) == 0

    def test_flat(self):
        assert trap([3, 3, 3, 3]) == 0

    def test_ascending(self):
        """No water - no barrier on the right to trap against."""
        assert trap([1, 2, 3, 4, 5]) == 0

    def test_descending(self):
        """No water - no barrier on the left to trap against."""
        assert trap([5, 4, 3, 2, 1]) == 0

    def test_peak(self):
        assert trap([0, 5, 0]) == 0

    def test_bowl(self):
        assert trap([5, 0, 5]) == 5

    def test_multiple_pools(self):
        assert trap([3, 0, 2, 0, 4]) == 7


class TestPrefixMaxMatch:
    """Prefix max approach should agree with two-pointer."""

    @pytest.mark.parametrize(
        "heights",
        [
            [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1],
            [4, 2, 0, 3, 2, 5],
            [1, 0, 1],
            [],
            [5],
            [3, 3, 3],
            [3, 0, 2, 0, 4],
            [5, 0, 5],
        ],
    )
    def test_matches_optimal(self, heights):
        assert trap_prefix_max(heights) == trap(heights)
