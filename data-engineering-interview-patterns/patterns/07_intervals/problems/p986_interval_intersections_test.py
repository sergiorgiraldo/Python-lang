"""Tests for LeetCode 986: Interval List Intersections."""

import pytest
from p986_interval_intersections import (
    interval_intersection,
    interval_intersection_brute,
)


class TestIntervalIntersection:
    @pytest.mark.parametrize("fn", [interval_intersection, interval_intersection_brute])
    def test_example(self, fn):
        a = [[0, 2], [5, 10], [13, 23], [24, 25]]
        b = [[1, 5], [8, 12], [15, 24], [25, 26]]
        assert fn(a, b) == [[1, 2], [5, 5], [8, 10], [15, 23], [24, 24], [25, 25]]

    @pytest.mark.parametrize("fn", [interval_intersection, interval_intersection_brute])
    def test_no_intersection(self, fn):
        assert fn([[1, 3], [5, 7]], [[8, 10], [12, 14]]) == []

    @pytest.mark.parametrize("fn", [interval_intersection, interval_intersection_brute])
    def test_one_empty(self, fn):
        assert fn([], [[1, 5]]) == []
        assert fn([[1, 5]], []) == []

    @pytest.mark.parametrize("fn", [interval_intersection, interval_intersection_brute])
    def test_both_empty(self, fn):
        assert fn([], []) == []

    @pytest.mark.parametrize("fn", [interval_intersection, interval_intersection_brute])
    def test_full_overlap(self, fn):
        assert fn([[0, 10]], [[0, 10]]) == [[0, 10]]

    @pytest.mark.parametrize("fn", [interval_intersection, interval_intersection_brute])
    def test_contained(self, fn):
        assert fn([[0, 10]], [[3, 5]]) == [[3, 5]]

    @pytest.mark.parametrize("fn", [interval_intersection, interval_intersection_brute])
    def test_touching_point(self, fn):
        """Single point intersection."""
        assert fn([[1, 3]], [[3, 5]]) == [[3, 3]]

    @pytest.mark.parametrize("fn", [interval_intersection, interval_intersection_brute])
    def test_multiple_intersections_with_one(self, fn):
        """One large interval intersects several small ones."""
        assert fn([[0, 100]], [[10, 20], [30, 40], [50, 60]]) == [
            [10, 20],
            [30, 40],
            [50, 60],
        ]
