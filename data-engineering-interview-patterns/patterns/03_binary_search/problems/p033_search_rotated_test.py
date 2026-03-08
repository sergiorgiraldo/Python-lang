"""Tests for LeetCode 33: Search in Rotated Sorted Array."""

import pytest
from p033_search_rotated import search, search_with_pivot


class TestSearch:
    """Test single-pass rotated binary search."""

    def test_found_in_right_half(self):
        assert search([4, 5, 6, 7, 0, 1, 2], 0) == 4

    def test_not_found(self):
        assert search([4, 5, 6, 7, 0, 1, 2], 3) == -1

    def test_single_not_found(self):
        assert search([1], 0) == -1

    def test_single_found(self):
        assert search([1], 1) == 0

    def test_found_in_left_half(self):
        assert search([4, 5, 6, 7, 0, 1, 2], 5) == 1

    def test_first_element(self):
        assert search([4, 5, 6, 7, 0, 1, 2], 4) == 0

    def test_last_element(self):
        assert search([4, 5, 6, 7, 0, 1, 2], 2) == 6

    def test_two_elements_found(self):
        assert search([1, 3], 3) == 1

    def test_two_elements_not_found(self):
        assert search([1, 3], 2) == -1

    def test_two_elements_rotated(self):
        assert search([3, 1], 1) == 1
        assert search([3, 1], 3) == 0

    def test_not_rotated(self):
        assert search([1, 2, 3, 4, 5], 3) == 2

    def test_all_positions(self):
        """Find every element in the rotated array."""
        nums = [4, 5, 6, 7, 0, 1, 2]
        for i, val in enumerate(nums):
            assert search(nums, val) == i

    def test_empty(self):
        assert search([], 1) == -1


class TestPivotApproach:
    """Two-pass approach should agree with single-pass."""

    @pytest.mark.parametrize(
        "nums,target",
        [
            ([4, 5, 6, 7, 0, 1, 2], 0),
            ([4, 5, 6, 7, 0, 1, 2], 3),
            ([4, 5, 6, 7, 0, 1, 2], 5),
            ([4, 5, 6, 7, 0, 1, 2], 4),
            ([1], 0),
            ([1], 1),
            ([3, 1], 1),
            ([1, 2, 3, 4, 5], 3),
        ],
    )
    def test_matches_single_pass(self, nums, target):
        assert search_with_pivot(nums, target) == search(nums, target)
