"""Tests for LeetCode 56: Merge Intervals."""

import pytest
from p056_merge_intervals import merge, merge_brute


class TestMerge:
    def test_example_1(self):
        assert merge([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]

    def test_example_2(self):
        assert merge([[1, 4], [4, 5]]) == [[1, 5]]

    def test_empty(self):
        assert merge([]) == []

    def test_single(self):
        assert merge([[1, 5]]) == [[1, 5]]

    def test_no_overlap(self):
        assert merge([[1, 2], [4, 5], [7, 8]]) == [[1, 2], [4, 5], [7, 8]]

    def test_all_overlap(self):
        assert merge([[1, 10], [2, 5], [3, 7], [6, 8]]) == [[1, 10]]

    def test_contained(self):
        """Smaller interval fully inside larger one."""
        assert merge([[1, 10], [3, 5]]) == [[1, 10]]

    def test_unsorted(self):
        assert merge([[3, 5], [1, 4]]) == [[1, 5]]

    def test_touching(self):
        """end == start of next → merge (they share a point)."""
        assert merge([[1, 3], [3, 5]]) == [[1, 5]]

    def test_chain_merge(self):
        """Multiple intervals chain-merge into one."""
        assert merge([[1, 3], [2, 5], [4, 7], [6, 9]]) == [[1, 9]]

    def test_same_start(self):
        assert merge([[1, 5], [1, 3]]) == [[1, 5]]

    def test_duplicate_intervals(self):
        assert merge([[1, 5], [1, 5]]) == [[1, 5]]


class TestMergeBrute:
    @pytest.mark.parametrize(
        "intervals, expected",
        [
            ([[1, 3], [2, 6], [8, 10], [15, 18]], [[1, 6], [8, 10], [15, 18]]),
            ([[1, 4], [4, 5]], [[1, 5]]),
            ([], []),
            ([[1, 5]], [[1, 5]]),
            ([[1, 10], [2, 5], [3, 7]], [[1, 10]]),
        ],
    )
    def test_matches_optimal(self, intervals, expected):
        assert merge([iv[:] for iv in intervals]) == expected
        assert merge_brute([iv[:] for iv in intervals]) == expected
