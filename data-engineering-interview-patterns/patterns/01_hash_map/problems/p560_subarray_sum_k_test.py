"""Tests for LeetCode 560: Subarray Sum Equals K."""

import pytest
from p560_subarray_sum_k import subarray_sum, subarray_sum_brute


class TestSubarraySum:
    """Test the prefix sum + hash map solution."""

    def test_basic_case(self):
        assert subarray_sum([1, 1, 1], 2) == 2

    def test_multiple_ways(self):
        """[1,2,3] has two subarrays summing to 3: [1,2] and [3]."""
        assert subarray_sum([1, 2, 3], 3) == 2

    def test_with_negatives(self):
        """Negative numbers create more possible subarrays."""
        assert subarray_sum([1, -1, 0], 0) == 3

    def test_single_element_match(self):
        assert subarray_sum([5], 5) == 1

    def test_single_element_no_match(self):
        assert subarray_sum([5], 3) == 0

    def test_all_zeros_target_zero(self):
        """Every subarray sums to zero: n*(n+1)/2 subarrays."""
        assert subarray_sum([0, 0, 0], 0) == 6

    def test_negative_target(self):
        assert subarray_sum([-1, -1, 1], -2) == 1

    def test_entire_array(self):
        """The whole array is the matching subarray."""
        assert subarray_sum([1, 2, 3], 6) == 1

    def test_no_match(self):
        assert subarray_sum([1, 2, 3], 100) == 0

    def test_prefix_sum_reuse(self):
        """Same prefix sum appears multiple times."""
        assert subarray_sum([1, -1, 1, -1], 0) == 4


class TestBruteForceMatch:
    """Brute force should agree with optimal on all inputs."""

    @pytest.mark.parametrize(
        "nums, k",
        [
            ([1, 1, 1], 2),
            ([1, 2, 3], 3),
            ([1, -1, 0], 0),
            ([5], 5),
            ([0, 0, 0], 0),
            ([-1, -1, 1], -2),
            ([1, -1, 1, -1], 0),
        ],
    )
    def test_matches_optimal(self, nums, k):
        assert subarray_sum_brute(nums, k) == subarray_sum(nums, k)
