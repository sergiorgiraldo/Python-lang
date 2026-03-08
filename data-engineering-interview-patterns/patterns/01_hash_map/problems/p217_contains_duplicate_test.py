"""Tests for LeetCode 217: Contains Duplicate."""

import pytest
from p217_contains_duplicate import (
    contains_duplicate,
    contains_duplicate_set,
    contains_duplicate_sort,
)


class TestContainsDuplicate:
    """Test the set-length comparison solution."""

    def test_has_duplicates(self):
        assert contains_duplicate([1, 2, 3, 1]) is True

    def test_no_duplicates(self):
        assert contains_duplicate([1, 2, 3, 4]) is False

    def test_many_duplicates(self):
        assert contains_duplicate([1, 1, 1, 3, 3, 4, 3, 2, 4, 2]) is True

    def test_empty_array(self):
        assert contains_duplicate([]) is False

    def test_single_element(self):
        assert contains_duplicate([1]) is False

    def test_two_same(self):
        assert contains_duplicate([1, 1]) is True

    def test_two_different(self):
        assert contains_duplicate([1, 2]) is False

    def test_negative_numbers(self):
        assert contains_duplicate([-1, -2, -1]) is True


class TestAllApproaches:
    """All three approaches should agree on every input."""

    @pytest.mark.parametrize(
        "nums, expected",
        [
            ([1, 2, 3, 1], True),
            ([1, 2, 3, 4], False),
            ([1, 1, 1, 3, 3, 4, 3, 2, 4, 2], True),
            ([], False),
            ([1], False),
            ([-1, -2, -1], True),
        ],
    )
    def test_approaches_agree(self, nums, expected):
        assert contains_duplicate(nums) is expected
        assert contains_duplicate_set(nums) is expected
        assert contains_duplicate_sort(nums) is expected
