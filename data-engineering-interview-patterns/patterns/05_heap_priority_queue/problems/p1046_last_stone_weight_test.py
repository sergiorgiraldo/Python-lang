"""Tests for LeetCode 1046: Last Stone Weight."""

import pytest
from p1046_last_stone_weight import last_stone_weight, last_stone_weight_sort


class TestLastStoneWeight:
    """Test the heap-based solution."""

    def test_example_case(self):
        assert last_stone_weight([2, 7, 4, 1, 8, 1]) == 1

    def test_single_stone(self):
        assert last_stone_weight([1]) == 1

    def test_two_equal_stones(self):
        """Equal stones destroy each other."""
        assert last_stone_weight([3, 3]) == 0

    def test_two_unequal_stones(self):
        assert last_stone_weight([3, 7]) == 4

    def test_all_same(self):
        """Even count of same stones → 0."""
        assert last_stone_weight([5, 5, 5, 5]) == 0

    def test_all_same_odd(self):
        """Odd count of same stones → one remains."""
        assert last_stone_weight([5, 5, 5]) == 5

    def test_large_and_small(self):
        assert last_stone_weight([10, 4, 2, 10]) == 2

    def test_descending_order(self):
        assert last_stone_weight([8, 4, 2, 1]) == 1

    def test_single_large_stone(self):
        assert last_stone_weight([100, 1, 1, 1]) == 97


class TestLastStoneWeightSort:
    """Verify brute force matches optimal."""

    @pytest.mark.parametrize(
        "stones, expected",
        [
            ([2, 7, 4, 1, 8, 1], 1),
            ([1], 1),
            ([3, 3], 0),
            ([3, 7], 4),
            ([5, 5, 5, 5], 0),
            ([5, 5, 5], 5),
            ([10, 4, 2, 10], 2),
        ],
    )
    def test_matches_optimal(self, stones, expected):
        assert last_stone_weight(list(stones)) == expected
        assert last_stone_weight_sort(list(stones)) == expected
