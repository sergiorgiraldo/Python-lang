"""Tests for LeetCode 977: Squares of a Sorted Array."""

import pytest
from p977_squares_sorted import sorted_squares, sorted_squares_simple


class TestSortedSquares:
    """Test the opposite-ends solution."""

    def test_mixed(self):
        assert sorted_squares([-4, -1, 0, 3, 10]) == [0, 1, 9, 16, 100]

    def test_mixed_duplicates(self):
        assert sorted_squares([-7, -3, 2, 3, 11]) == [4, 9, 9, 49, 121]

    def test_all_positive(self):
        assert sorted_squares([0, 1, 2]) == [0, 1, 4]

    def test_all_negative(self):
        assert sorted_squares([-5, -3, -1]) == [1, 9, 25]

    def test_single(self):
        assert sorted_squares([5]) == [25]

    def test_single_negative(self):
        assert sorted_squares([-5]) == [25]

    def test_single_zero(self):
        assert sorted_squares([0]) == [0]

    def test_symmetric(self):
        assert sorted_squares([-3, -2, -1, 1, 2, 3]) == [1, 1, 4, 4, 9, 9]

    def test_two_elements(self):
        assert sorted_squares([-1, 2]) == [1, 4]


class TestSimpleMatch:
    """Simple approach should match optimal."""

    @pytest.mark.parametrize(
        "nums",
        [
            [-4, -1, 0, 3, 10],
            [-7, -3, 2, 3, 11],
            [0, 1, 2],
            [-5, -3, -1],
            [-3, -2, -1, 1, 2, 3],
        ],
    )
    def test_matches_optimal(self, nums):
        assert sorted_squares_simple(nums) == sorted_squares(nums)
