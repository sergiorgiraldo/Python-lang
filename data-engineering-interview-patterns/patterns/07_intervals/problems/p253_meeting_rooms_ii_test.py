"""Tests for LeetCode 253: Meeting Rooms II."""

import pytest
from p253_meeting_rooms_ii import min_meeting_rooms_heap, min_meeting_rooms_sweep


class TestMinMeetingRooms:
    @pytest.mark.parametrize("fn", [min_meeting_rooms_heap, min_meeting_rooms_sweep])
    def test_example_1(self, fn):
        assert fn([[0, 30], [5, 10], [15, 20]]) == 2

    @pytest.mark.parametrize("fn", [min_meeting_rooms_heap, min_meeting_rooms_sweep])
    def test_no_overlap(self, fn):
        assert fn([[7, 10], [2, 4]]) == 1

    @pytest.mark.parametrize("fn", [min_meeting_rooms_heap, min_meeting_rooms_sweep])
    def test_empty(self, fn):
        assert fn([]) == 0

    @pytest.mark.parametrize("fn", [min_meeting_rooms_heap, min_meeting_rooms_sweep])
    def test_single(self, fn):
        assert fn([[1, 5]]) == 1

    @pytest.mark.parametrize("fn", [min_meeting_rooms_heap, min_meeting_rooms_sweep])
    def test_all_overlap(self, fn):
        assert fn([[1, 10], [2, 9], [3, 8]]) == 3

    @pytest.mark.parametrize("fn", [min_meeting_rooms_heap, min_meeting_rooms_sweep])
    def test_chain(self, fn):
        """Meetings overlap in pairs but not all three simultaneously."""
        assert fn([[1, 5], [4, 8], [7, 10]]) == 2

    @pytest.mark.parametrize("fn", [min_meeting_rooms_heap, min_meeting_rooms_sweep])
    def test_back_to_back(self, fn):
        """End time == start time of next: room can be reused."""
        assert fn([[1, 5], [5, 10], [10, 15]]) == 1

    @pytest.mark.parametrize("fn", [min_meeting_rooms_heap, min_meeting_rooms_sweep])
    def test_same_time(self, fn):
        assert fn([[1, 5], [1, 5], [1, 5]]) == 3

    @pytest.mark.parametrize("fn", [min_meeting_rooms_heap, min_meeting_rooms_sweep])
    def test_staggered(self, fn):
        assert fn([[1, 5], [2, 3], [4, 6], [5, 7]]) == 2
