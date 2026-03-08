"""Tests for LeetCode 347: Top K Frequent Elements."""

import pytest
from p347_top_k_frequent import (
    top_k_frequent,
    top_k_frequent_bucket,
    top_k_frequent_heap,
)


class TestTopKFrequent:
    """Test the Counter.most_common solution."""

    def test_basic_case(self):
        assert set(top_k_frequent([1, 1, 1, 2, 2, 3], 2)) == {1, 2}

    def test_single_element(self):
        assert top_k_frequent([1], 1) == [1]

    def test_k_equals_unique_count(self):
        """When k equals the number of unique elements, return all."""
        result = top_k_frequent([1, 2, 3], 3)
        assert set(result) == {1, 2, 3}

    def test_negative_numbers(self):
        assert set(top_k_frequent([4, 1, -1, 2, -1, 2, 3], 2)) == {-1, 2}

    def test_all_same(self):
        assert top_k_frequent([5, 5, 5, 5], 1) == [5]

    def test_tie_in_frequency(self):
        """When elements tie in frequency, any k of them is valid."""
        result = top_k_frequent([1, 2, 3, 4], 2)
        assert len(result) == 2
        assert all(x in [1, 2, 3, 4] for x in result)


class TestAllApproaches:
    """All approaches should return the same set of elements."""

    @pytest.mark.parametrize(
        "nums, k, expected_set",
        [
            ([1, 1, 1, 2, 2, 3], 2, {1, 2}),
            ([1], 1, {1}),
            ([4, 1, -1, 2, -1, 2, 3], 2, {-1, 2}),
            ([5, 5, 5, 5], 1, {5}),
        ],
    )
    def test_approaches_agree(self, nums, k, expected_set):
        assert set(top_k_frequent(nums, k)) == expected_set
        assert set(top_k_frequent_heap(nums, k)) == expected_set
        assert set(top_k_frequent_bucket(nums, k)) == expected_set
