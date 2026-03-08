"""Tests for LeetCode 239: Sliding Window Maximum."""

import pytest
from p239_sliding_window_max import max_sliding_window, max_sliding_window_brute


class TestMaxSlidingWindow:
    """Test the monotonic deque approach."""

    def test_basic(self):
        assert max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3) == [
            3,
            3,
            5,
            5,
            6,
            7,
        ]

    def test_single_element(self):
        assert max_sliding_window([1], 1) == [1]

    def test_window_size_one(self):
        assert max_sliding_window([1, -1], 1) == [1, -1]

    def test_descending(self):
        """Max is always the leftmost element in the window."""
        assert max_sliding_window([9, 8, 7, 6, 5], 3) == [9, 8, 7]

    def test_ascending(self):
        """Max is always the rightmost element in the window."""
        assert max_sliding_window([1, 2, 3, 4, 5], 3) == [3, 4, 5]

    def test_window_equals_array(self):
        assert max_sliding_window([3, 1, 2], 3) == [3]

    def test_all_same(self):
        assert max_sliding_window([5, 5, 5, 5], 2) == [5, 5, 5]

    def test_negative_values(self):
        assert max_sliding_window([-1, -3, -5, -2, -4], 3) == [-1, -2, -2]

    def test_large_then_small(self):
        """Large value dominates until it leaves the window."""
        assert max_sliding_window([10, 1, 1, 1, 1], 3) == [10, 1, 1]

    def test_alternating(self):
        assert max_sliding_window([1, 5, 1, 5, 1], 2) == [5, 5, 5, 5]

    def test_window_size_two(self):
        assert max_sliding_window([4, 3, 2, 1, 5], 2) == [4, 3, 2, 5]


class TestBruteForceMatch:
    """Brute force should agree with deque approach."""

    @pytest.mark.parametrize(
        "nums,k",
        [
            ([1, 3, -1, -3, 5, 3, 6, 7], 3),
            ([1], 1),
            ([9, 8, 7, 6, 5], 3),
            ([1, 2, 3, 4, 5], 3),
            ([5, 5, 5, 5], 2),
            ([-1, -3, -5, -2, -4], 3),
            ([10, 1, 1, 1, 1], 3),
            ([1, 5, 1, 5, 1], 2),
        ],
    )
    def test_matches_deque(self, nums, k):
        assert max_sliding_window_brute(nums, k) == max_sliding_window(nums, k)
