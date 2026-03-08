"""Tests for LeetCode 74: Search a 2D Matrix."""

import pytest
from p074_search_2d_matrix import search_matrix, search_matrix_two_binary

MATRIX = [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]]


class TestSearchMatrix:
    """Test the flattened binary search."""

    def test_found(self):
        assert search_matrix(MATRIX, 3) is True

    def test_not_found(self):
        assert search_matrix(MATRIX, 13) is False

    def test_first_element(self):
        assert search_matrix(MATRIX, 1) is True

    def test_last_element(self):
        assert search_matrix(MATRIX, 60) is True

    def test_row_boundary(self):
        """Target is last in one row, first in next."""
        assert search_matrix(MATRIX, 7) is True
        assert search_matrix(MATRIX, 10) is True

    def test_single_element_found(self):
        assert search_matrix([[1]], 1) is True

    def test_single_element_not_found(self):
        assert search_matrix([[1]], 2) is False

    def test_empty_matrix(self):
        assert search_matrix([], 1) is False

    def test_empty_row(self):
        assert search_matrix([[]], 1) is False

    def test_single_row(self):
        assert search_matrix([[1, 3, 5]], 3) is True
        assert search_matrix([[1, 3, 5]], 4) is False

    def test_single_column(self):
        assert search_matrix([[1], [5], [10]], 5) is True
        assert search_matrix([[1], [5], [10]], 7) is False


class TestTwoBinaryMatch:
    """Two-binary-search approach should agree."""

    @pytest.mark.parametrize(
        "target,expected",
        [
            (3, True),
            (13, False),
            (1, True),
            (60, True),
            (7, True),
            (10, True),
        ],
    )
    def test_matches_flattened(self, target, expected):
        assert search_matrix_two_binary(MATRIX, target) == expected
