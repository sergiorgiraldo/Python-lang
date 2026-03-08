"""Tests for LeetCode 23: Merge K Sorted Lists."""

import pytest
from p023_merge_k_sorted import (
    build_linked_list,
    linked_list_to_array,
    merge_k_sorted_arrays,
    merge_k_sorted_brute,
    merge_k_sorted_lazy,
    merge_k_sorted_lists,
    merge_k_sorted_sequential,
)


class TestMergeKSortedLists:
    """Test the linked list heap merge."""

    def test_example_case(self):
        lists = [
            build_linked_list([1, 4, 5]),
            build_linked_list([1, 3, 4]),
            build_linked_list([2, 6]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linked_list_to_array(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_input(self):
        assert merge_k_sorted_lists([]) is None

    def test_all_empty_lists(self):
        assert merge_k_sorted_lists([None, None, None]) is None

    def test_single_list(self):
        lists = [build_linked_list([1, 2, 3])]
        result = merge_k_sorted_lists(lists)
        assert linked_list_to_array(result) == [1, 2, 3]

    def test_some_empty(self):
        lists = [
            build_linked_list([1, 3]),
            None,
            build_linked_list([2, 4]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linked_list_to_array(result) == [1, 2, 3, 4]

    def test_single_element_lists(self):
        lists = [
            build_linked_list([5]),
            build_linked_list([2]),
            build_linked_list([8]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linked_list_to_array(result) == [2, 5, 8]

    def test_duplicates_across_lists(self):
        lists = [
            build_linked_list([1, 1]),
            build_linked_list([1, 1]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linked_list_to_array(result) == [1, 1, 1, 1]


class TestMergeKSortedArrays:
    """Test the array-based heap merge."""

    def test_example_case(self):
        assert merge_k_sorted_arrays([[1, 4, 5], [1, 3, 4], [2, 6]]) == [
            1,
            1,
            2,
            3,
            4,
            4,
            5,
            6,
        ]

    def test_empty_input(self):
        assert merge_k_sorted_arrays([]) == []

    def test_empty_lists(self):
        assert merge_k_sorted_arrays([[], [], []]) == []

    def test_single_list(self):
        assert merge_k_sorted_arrays([[1, 2, 3]]) == [1, 2, 3]

    def test_two_lists(self):
        assert merge_k_sorted_arrays([[1, 3, 5], [2, 4, 6]]) == [1, 2, 3, 4, 5, 6]

    def test_many_lists(self):
        lists = [[i, i + 10] for i in range(5)]
        result = merge_k_sorted_arrays(lists)
        assert result == sorted(result)
        assert len(result) == 10

    def test_negative_numbers(self):
        assert merge_k_sorted_arrays([[-3, -1], [-2, 0], [-5, 5]]) == [
            -5,
            -3,
            -2,
            -1,
            0,
            5,
        ]

    def test_uneven_lengths(self):
        assert merge_k_sorted_arrays([[1], [2, 3, 4, 5], [6]]) == [1, 2, 3, 4, 5, 6]


class TestMergeKSortedLazy:
    """Test the generator-based merge."""

    def test_basic(self):
        result = list(merge_k_sorted_lazy([[1, 4, 5], [1, 3, 4], [2, 6]]))
        assert result == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty(self):
        assert list(merge_k_sorted_lazy([])) == []

    def test_generators_as_input(self):
        """Verify it works with actual generators, not just lists."""
        gen1 = (x for x in [1, 3, 5])
        gen2 = (x for x in [2, 4, 6])
        result = list(merge_k_sorted_lazy([gen1, gen2]))
        assert result == [1, 2, 3, 4, 5, 6]

    def test_partial_consumption(self):
        """Can stop consuming early without processing everything."""
        gen = merge_k_sorted_lazy([[1, 3, 5, 7, 9], [2, 4, 6, 8, 10]])
        first_three = [next(gen), next(gen), next(gen)]
        assert first_three == [1, 2, 3]


class TestAllArrayApproaches:
    """All array approaches should produce the same result."""

    @pytest.mark.parametrize(
        "lists, expected",
        [
            ([[1, 4, 5], [1, 3, 4], [2, 6]], [1, 1, 2, 3, 4, 4, 5, 6]),
            ([], []),
            ([[], [], []], []),
            ([[1, 2, 3]], [1, 2, 3]),
            ([[1, 3, 5], [2, 4, 6]], [1, 2, 3, 4, 5, 6]),
            ([[-3, -1], [-2, 0]], [-3, -2, -1, 0]),
        ],
    )
    def test_approaches_agree(self, lists, expected):
        assert merge_k_sorted_arrays([list(sub) for sub in lists]) == expected
        assert merge_k_sorted_brute([list(sub) for sub in lists]) == expected
        assert merge_k_sorted_sequential([list(sub) for sub in lists]) == expected
        assert list(merge_k_sorted_lazy([list(sub) for sub in lists])) == expected
