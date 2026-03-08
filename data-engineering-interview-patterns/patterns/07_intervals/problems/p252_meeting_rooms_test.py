"""Tests for LeetCode 252: Meeting Rooms."""

import pytest
from p252_meeting_rooms import can_attend, can_attend_brute


class TestCanAttend:
    @pytest.mark.parametrize("fn", [can_attend, can_attend_brute])
    def test_overlap(self, fn):
        assert fn([[0, 30], [5, 10], [15, 20]]) is False

    @pytest.mark.parametrize("fn", [can_attend, can_attend_brute])
    def test_no_overlap(self, fn):
        assert fn([[7, 10], [2, 4]]) is True

    @pytest.mark.parametrize("fn", [can_attend, can_attend_brute])
    def test_empty(self, fn):
        assert fn([]) is True

    @pytest.mark.parametrize("fn", [can_attend, can_attend_brute])
    def test_single_meeting(self, fn):
        assert fn([[1, 5]]) is True

    @pytest.mark.parametrize("fn", [can_attend, can_attend_brute])
    def test_adjacent_no_overlap(self, fn):
        """Back-to-back meetings: end == start of next is NOT overlap."""
        assert fn([[1, 5], [5, 10]]) is True

    @pytest.mark.parametrize("fn", [can_attend, can_attend_brute])
    def test_contained(self, fn):
        """One meeting fully inside another."""
        assert fn([[1, 10], [3, 5]]) is False

    @pytest.mark.parametrize("fn", [can_attend, can_attend_brute])
    def test_many_non_overlapping(self, fn):
        intervals = [[i * 10, i * 10 + 5] for i in range(10)]
        assert fn(intervals) is True

    @pytest.mark.parametrize("fn", [can_attend, can_attend_brute])
    def test_same_time(self, fn):
        assert fn([[1, 5], [1, 5]]) is False

    @pytest.mark.parametrize("fn", [can_attend, can_attend_brute])
    def test_unsorted_input(self, fn):
        """Input not sorted - algorithm should handle this."""
        assert fn([[15, 20], [0, 5], [10, 15]]) is True
