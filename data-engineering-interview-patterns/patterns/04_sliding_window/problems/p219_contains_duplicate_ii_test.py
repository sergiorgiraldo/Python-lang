"""Tests for LeetCode 219: Contains Duplicate II."""

import pytest
from p219_contains_duplicate_ii import (
    contains_nearby_duplicate,
    contains_nearby_duplicate_brute,
)


class TestContainsNearbyDuplicate:
    """Test the sliding window + hash set approach."""

    def test_duplicate_within_k(self):
        assert contains_nearby_duplicate([1, 2, 3, 1], 3) is True

    def test_adjacent_duplicate(self):
        assert contains_nearby_duplicate([1, 0, 1, 1], 1) is True

    def test_duplicate_outside_k(self):
        assert contains_nearby_duplicate([1, 2, 3, 1, 2, 3], 2) is False

    def test_no_duplicates(self):
        assert contains_nearby_duplicate([1, 2, 3, 4], 3) is False

    def test_empty(self):
        assert contains_nearby_duplicate([], 0) is False

    def test_single_element(self):
        assert contains_nearby_duplicate([1], 1) is False

    def test_all_same(self):
        assert contains_nearby_duplicate([1, 1, 1, 1], 1) is True

    def test_k_zero(self):
        """k=0 means same index - no distinct pair possible."""
        assert contains_nearby_duplicate([1, 1], 0) is False

    def test_k_larger_than_array(self):
        assert contains_nearby_duplicate([1, 2, 1], 10) is True

    def test_duplicate_exactly_at_k(self):
        """Distance equals k exactly - should return True."""
        assert contains_nearby_duplicate([1, 2, 3, 4, 1], 4) is True

    def test_duplicate_at_k_plus_one(self):
        """Distance is k+1 - should return False."""
        assert contains_nearby_duplicate([1, 2, 3, 4, 5, 1], 4) is False


class TestBruteForceMatch:
    """Brute force should agree with sliding window."""

    @pytest.mark.parametrize(
        "nums,k",
        [
            ([1, 2, 3, 1], 3),
            ([1, 0, 1, 1], 1),
            ([1, 2, 3, 1, 2, 3], 2),
            ([1, 2, 3, 4], 3),
            ([1, 1, 1, 1], 1),
            ([1, 2, 3, 4, 1], 4),
            ([1, 2, 3, 4, 5, 1], 4),
        ],
    )
    def test_matches_sliding(self, nums, k):
        assert contains_nearby_duplicate_brute(nums, k) == contains_nearby_duplicate(
            nums, k
        )
