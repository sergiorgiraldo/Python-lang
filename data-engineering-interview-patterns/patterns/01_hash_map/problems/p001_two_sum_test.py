"""Tests for LeetCode 1: Two Sum."""

import pytest
from p001_two_sum import two_sum, two_sum_brute


class TestTwoSum:
    """Test the optimal hash map solution."""

    def test_basic_case(self):
        assert two_sum([2, 7, 11, 15], 9) == [0, 1]

    def test_negative_numbers(self):
        assert two_sum([-1, -2, -3, -4], -6) == [1, 3]

    def test_zero_in_array(self):
        """Zero is a valid value, not a special case."""
        assert two_sum([0, 4, 3, 0], 0) == [0, 3]

    def test_duplicate_values(self):
        """Same value at different indices."""
        assert two_sum([3, 3], 6) == [0, 1]

    def test_solution_at_end(self):
        assert two_sum([1, 2, 3, 4], 7) == [2, 3]

    def test_large_numbers(self):
        assert two_sum([10**9, -(10**9), 5, 3], 8) == [2, 3]

    def test_no_solution(self):
        assert two_sum([1, 2, 3], 100) == []


class TestTwoSumBrute:
    """Verify brute force matches optimal on shared cases."""

    @pytest.mark.parametrize(
        "nums, target, expected",
        [
            ([2, 7, 11, 15], 9, [0, 1]),
            ([-1, -2, -3, -4], -6, [1, 3]),
            ([3, 3], 6, [0, 1]),
            ([1, 2, 3], 100, []),
        ],
    )
    def test_matches_optimal(self, nums, target, expected):
        assert two_sum_brute(nums, target) == expected
