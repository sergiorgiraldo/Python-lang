"""Tests for LeetCode 128: Longest Consecutive Sequence."""

import pytest
from p128_longest_consecutive import longest_consecutive, longest_consecutive_sort


class TestLongestConsecutive:
    """Test the set-based O(n) solution."""

    def test_basic_case(self):
        assert longest_consecutive([100, 4, 200, 1, 3, 2]) == 4

    def test_long_sequence(self):
        assert longest_consecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]) == 9

    def test_empty_array(self):
        assert longest_consecutive([]) == 0

    def test_single_element(self):
        assert longest_consecutive([1]) == 1

    def test_no_consecutive(self):
        assert longest_consecutive([10, 20, 30]) == 1

    def test_duplicates(self):
        """Duplicates should not affect sequence length."""
        assert longest_consecutive([1, 2, 0, 1]) == 3

    def test_negative_numbers(self):
        assert longest_consecutive([-3, -2, -1, 0, 1]) == 5

    def test_all_same(self):
        assert longest_consecutive([5, 5, 5, 5]) == 1

    def test_two_separate_sequences(self):
        assert longest_consecutive([1, 2, 3, 10, 11, 12, 13]) == 4


class TestLongestConsecutiveSort:
    """Verify sort-based approach matches optimal."""

    @pytest.mark.parametrize(
        "nums, expected",
        [
            ([100, 4, 200, 1, 3, 2], 4),
            ([0, 3, 7, 2, 5, 8, 4, 6, 0, 1], 9),
            ([], 0),
            ([1], 1),
            ([1, 2, 0, 1], 3),
            ([-3, -2, -1, 0, 1], 5),
        ],
    )
    def test_matches_optimal(self, nums, expected):
        assert longest_consecutive_sort(nums) == expected
