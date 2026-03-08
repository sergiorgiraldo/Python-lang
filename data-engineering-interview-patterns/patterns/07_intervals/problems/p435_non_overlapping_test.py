"""Tests for LeetCode 435: Non-overlapping Intervals."""

import pytest
from p435_non_overlapping import (
    erase_overlap_intervals,
    erase_overlap_intervals_start,
)


class TestEraseOverlapIntervals:
    @pytest.mark.parametrize(
        "fn", [erase_overlap_intervals, erase_overlap_intervals_start]
    )
    def test_example_1(self, fn):
        assert fn([[1, 2], [2, 3], [3, 4], [1, 3]]) == 1

    @pytest.mark.parametrize(
        "fn", [erase_overlap_intervals, erase_overlap_intervals_start]
    )
    def test_example_2(self, fn):
        assert fn([[1, 2], [1, 2], [1, 2]]) == 2

    @pytest.mark.parametrize(
        "fn", [erase_overlap_intervals, erase_overlap_intervals_start]
    )
    def test_example_3(self, fn):
        assert fn([[1, 2], [2, 3]]) == 0

    @pytest.mark.parametrize(
        "fn", [erase_overlap_intervals, erase_overlap_intervals_start]
    )
    def test_empty(self, fn):
        assert fn([]) == 0

    @pytest.mark.parametrize(
        "fn", [erase_overlap_intervals, erase_overlap_intervals_start]
    )
    def test_single(self, fn):
        assert fn([[1, 5]]) == 0

    @pytest.mark.parametrize(
        "fn", [erase_overlap_intervals, erase_overlap_intervals_start]
    )
    def test_all_overlap(self, fn):
        assert fn([[1, 10], [2, 9], [3, 8]]) == 2

    @pytest.mark.parametrize(
        "fn", [erase_overlap_intervals, erase_overlap_intervals_start]
    )
    def test_no_overlap(self, fn):
        assert fn([[1, 2], [3, 4], [5, 6]]) == 0

    @pytest.mark.parametrize(
        "fn", [erase_overlap_intervals, erase_overlap_intervals_start]
    )
    def test_nested(self, fn):
        """Remove the outer interval, keep the inner ones."""
        assert fn([[1, 100], [11, 22], [33, 44], [55, 66]]) == 1

    @pytest.mark.parametrize(
        "fn", [erase_overlap_intervals, erase_overlap_intervals_start]
    )
    def test_same_start(self, fn):
        assert fn([[1, 5], [1, 3]]) == 1
