"""Tests for LeetCode 703: Kth Largest Element in a Stream."""

import pytest
from p703_kth_largest_stream import KthLargest, KthLargestSort


class TestKthLargest:
    """Test the heap-based solution."""

    def test_example_case(self):
        kth = KthLargest(3, [4, 5, 8, 2])
        assert kth.add(3) == 4
        assert kth.add(5) == 5
        assert kth.add(10) == 5
        assert kth.add(9) == 8
        assert kth.add(4) == 8

    def test_k_equals_1(self):
        """K=1 means always return the maximum."""
        kth = KthLargest(1, [])
        assert kth.add(5) == 5
        assert kth.add(3) == 5
        assert kth.add(10) == 10

    def test_empty_initial(self):
        """Start with no elements, build up via add."""
        kth = KthLargest(2, [])
        assert kth.add(1) == 1  # only 1 element, heap not full
        assert kth.add(2) == 1  # heap = [1, 2], 2nd largest = 1
        assert kth.add(3) == 2  # heap = [2, 3], 2nd largest = 2

    def test_all_same_values(self):
        kth = KthLargest(2, [5, 5, 5])
        assert kth.add(5) == 5
        assert kth.add(5) == 5

    def test_negative_numbers(self):
        kth = KthLargest(2, [-1, -2, -3])
        assert kth.add(-4) == -2
        assert kth.add(0) == -1
        assert kth.add(5) == 0

    def test_initial_list_larger_than_k(self):
        """Initial list has more than k elements."""
        kth = KthLargest(2, [10, 20, 30, 40])
        # Heap should hold [30, 40], kth largest = 30
        assert kth.add(5) == 30
        assert kth.add(50) == 40

    def test_initial_list_smaller_than_k(self):
        """Initial list has fewer than k elements."""
        kth = KthLargest(5, [1, 2])
        assert kth.add(3) == 1
        assert kth.add(4) == 1
        assert kth.add(5) == 1  # now heap is full, 5th largest = 1
        assert kth.add(6) == 2


class TestKthLargestSort:
    """Verify brute force matches optimal on shared cases."""

    @pytest.mark.parametrize(
        "k, init, adds, expected",
        [
            (3, [4, 5, 8, 2], [3, 5, 10, 9, 4], [4, 5, 5, 8, 8]),
            (1, [], [5, 3, 10], [5, 5, 10]),
            (2, [-1, -2, -3], [-4, 0, 5], [-2, -1, 0]),
        ],
    )
    def test_matches_optimal(self, k, init, adds, expected):
        kth_heap = KthLargest(k, list(init))
        kth_sort = KthLargestSort(k, list(init))
        for val, exp in zip(adds, expected):
            assert kth_heap.add(val) == exp
            assert kth_sort.add(val) == exp
