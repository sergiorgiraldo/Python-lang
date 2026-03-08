"""Tests for LeetCode 215: Kth Largest Element in an Array."""

import pytest
from p215_kth_largest_array import (
    find_kth_largest,
    find_kth_largest_nlargest,
    find_kth_largest_quickselect,
    find_kth_largest_sort,
)


class TestFindKthLargest:
    """Test the heap-based solution."""

    def test_example_1(self):
        assert find_kth_largest([3, 2, 1, 5, 6, 4], 2) == 5

    def test_example_2(self):
        assert find_kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4) == 4

    def test_single_element(self):
        assert find_kth_largest([1], 1) == 1

    def test_k_equals_n(self):
        """Kth largest where k = array length means the smallest."""
        assert find_kth_largest([3, 2, 1, 5, 6, 4], 6) == 1

    def test_k_equals_1(self):
        """K=1 means the maximum."""
        assert find_kth_largest([3, 2, 1, 5, 6, 4], 1) == 6

    def test_duplicates(self):
        assert find_kth_largest([3, 3, 3, 3], 2) == 3

    def test_negative_numbers(self):
        assert find_kth_largest([-1, -2, -3, -4], 2) == -2

    def test_mixed_signs(self):
        assert find_kth_largest([-1, 0, 1, 2, -2], 3) == 0

    def test_large_k(self):
        """Finding the smallest via kth largest."""
        assert find_kth_largest([5, 2, 8, 1, 9], 5) == 1


class TestAllApproaches:
    """All approaches should agree on every input."""

    @pytest.mark.parametrize(
        "nums, k, expected",
        [
            ([3, 2, 1, 5, 6, 4], 2, 5),
            ([3, 2, 3, 1, 2, 4, 5, 5, 6], 4, 4),
            ([1], 1, 1),
            ([3, 3, 3, 3], 2, 3),
            ([-1, -2, -3, -4], 2, -2),
            ([5, 2, 8, 1, 9], 5, 1),
        ],
    )
    def test_approaches_agree(self, nums, k, expected):
        assert find_kth_largest(list(nums), k) == expected
        assert find_kth_largest_sort(list(nums), k) == expected
        assert find_kth_largest_nlargest(list(nums), k) == expected
        assert find_kth_largest_quickselect(list(nums), k) == expected
