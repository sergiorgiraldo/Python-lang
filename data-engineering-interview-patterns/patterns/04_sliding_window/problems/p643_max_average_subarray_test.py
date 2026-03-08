"""Tests for LeetCode 643: Maximum Average Subarray I."""

import pytest
from p643_max_average_subarray import find_max_average, find_max_average_brute


class TestFindMaxAverage:
    """Test the fixed-window sliding average."""

    def test_basic(self):
        assert find_max_average([1, 12, -5, -6, 50, 3], 4) == pytest.approx(12.75)

    def test_single_element(self):
        assert find_max_average([5], 1) == pytest.approx(5.0)

    def test_window_equals_array(self):
        assert find_max_average([1, 2, 3], 3) == pytest.approx(2.0)

    def test_all_negative(self):
        assert find_max_average([-1, -2, -3, -4], 2) == pytest.approx(-1.5)

    def test_all_same(self):
        assert find_max_average([5, 5, 5, 5], 2) == pytest.approx(5.0)

    def test_window_size_one(self):
        assert find_max_average([0, 4, 0, 3, 2], 1) == pytest.approx(4.0)

    def test_max_at_end(self):
        assert find_max_average([1, 1, 1, 1, 10, 10], 2) == pytest.approx(10.0)

    def test_max_at_start(self):
        assert find_max_average([10, 10, 1, 1, 1, 1], 2) == pytest.approx(10.0)

    def test_negative_and_positive(self):
        assert find_max_average([-1, 3, -2, 5, -1], 3) == pytest.approx(2.0)


class TestBruteForceMatch:
    """Brute force should agree with sliding window."""

    @pytest.mark.parametrize(
        "nums,k",
        [
            ([1, 12, -5, -6, 50, 3], 4),
            ([5], 1),
            ([-1, -2, -3, -4], 2),
            ([1, 1, 1, 1, 10, 10], 2),
            ([-1, 3, -2, 5, -1], 3),
        ],
    )
    def test_matches_sliding(self, nums, k):
        assert find_max_average_brute(nums, k) == pytest.approx(
            find_max_average(nums, k)
        )
