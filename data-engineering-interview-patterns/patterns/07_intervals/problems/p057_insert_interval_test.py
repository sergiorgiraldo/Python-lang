"""Tests for LeetCode 57: Insert Interval."""

import pytest
from p057_insert_interval import insert, insert_binary_search


class TestInsert:
    @pytest.mark.parametrize("fn", [insert, insert_binary_search])
    def test_example_1(self, fn):
        assert fn([[1, 3], [6, 9]], [2, 5]) == [[1, 5], [6, 9]]

    @pytest.mark.parametrize("fn", [insert, insert_binary_search])
    def test_example_2(self, fn):
        result = fn([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8])
        assert result == [[1, 2], [3, 10], [12, 16]]

    @pytest.mark.parametrize("fn", [insert, insert_binary_search])
    def test_empty(self, fn):
        assert fn([], [5, 7]) == [[5, 7]]

    @pytest.mark.parametrize("fn", [insert, insert_binary_search])
    def test_no_overlap_before(self, fn):
        assert fn([[3, 5], [7, 9]], [1, 2]) == [[1, 2], [3, 5], [7, 9]]

    @pytest.mark.parametrize("fn", [insert, insert_binary_search])
    def test_no_overlap_after(self, fn):
        assert fn([[1, 3], [5, 7]], [8, 10]) == [[1, 3], [5, 7], [8, 10]]

    @pytest.mark.parametrize("fn", [insert, insert_binary_search])
    def test_merge_all(self, fn):
        assert fn([[1, 3], [5, 7], [9, 11]], [2, 10]) == [[1, 11]]

    @pytest.mark.parametrize("fn", [insert, insert_binary_search])
    def test_contained(self, fn):
        """New interval fully inside an existing one."""
        assert fn([[1, 10]], [3, 5]) == [[1, 10]]

    @pytest.mark.parametrize("fn", [insert, insert_binary_search])
    def test_containing(self, fn):
        """New interval fully contains an existing one."""
        assert fn([[3, 5]], [1, 10]) == [[1, 10]]

    @pytest.mark.parametrize("fn", [insert, insert_binary_search])
    def test_touching(self, fn):
        assert fn([[1, 3], [6, 9]], [3, 6]) == [[1, 9]]
