"""Tests for LeetCode 295: Find Median from Data Stream."""

import pytest
from p295_find_median_stream import MedianFinder, MedianFinderSort


class TestMedianFinder:
    """Test the two-heap solution."""

    def test_example_case(self):
        mf = MedianFinder()
        mf.add_num(1)
        mf.add_num(2)
        assert mf.find_median() == 1.5
        mf.add_num(3)
        assert mf.find_median() == 2.0

    def test_single_element(self):
        mf = MedianFinder()
        mf.add_num(5)
        assert mf.find_median() == 5.0

    def test_two_elements(self):
        mf = MedianFinder()
        mf.add_num(1)
        mf.add_num(2)
        assert mf.find_median() == 1.5

    def test_odd_count(self):
        mf = MedianFinder()
        for num in [3, 1, 2]:
            mf.add_num(num)
        assert mf.find_median() == 2.0

    def test_even_count(self):
        mf = MedianFinder()
        for num in [4, 3, 1, 2]:
            mf.add_num(num)
        assert mf.find_median() == 2.5

    def test_duplicates(self):
        mf = MedianFinder()
        for num in [5, 5, 5, 5]:
            mf.add_num(num)
        assert mf.find_median() == 5.0

    def test_negative_numbers(self):
        mf = MedianFinder()
        for num in [-1, -2, -3]:
            mf.add_num(num)
        assert mf.find_median() == -2.0

    def test_mixed_signs(self):
        mf = MedianFinder()
        for num in [-5, 0, 5]:
            mf.add_num(num)
        assert mf.find_median() == 0.0

    def test_increasing_stream(self):
        mf = MedianFinder()
        mf.add_num(1)
        assert mf.find_median() == 1.0
        mf.add_num(2)
        assert mf.find_median() == 1.5
        mf.add_num(3)
        assert mf.find_median() == 2.0
        mf.add_num(4)
        assert mf.find_median() == 2.5
        mf.add_num(5)
        assert mf.find_median() == 3.0

    def test_decreasing_stream(self):
        mf = MedianFinder()
        for num in [5, 4, 3, 2, 1]:
            mf.add_num(num)
        assert mf.find_median() == 3.0

    def test_large_values(self):
        mf = MedianFinder()
        for num in [10000, -10000]:
            mf.add_num(num)
        assert mf.find_median() == 0.0


class TestMedianFinderSort:
    """Verify brute force matches optimal."""

    @pytest.mark.parametrize(
        "stream, expected_medians",
        [
            ([1, 2, 3], [1.0, 1.5, 2.0]),
            ([5, 2, 8, 1, 9], [5.0, 3.5, 5.0, 3.5, 5.0]),
            ([3, 3, 3], [3.0, 3.0, 3.0]),
            ([-1, -2, -3], [-1.0, -1.5, -2.0]),
        ],
    )
    def test_matches_optimal(self, stream, expected_medians):
        mf_heap = MedianFinder()
        mf_sort = MedianFinderSort()
        for num, expected in zip(stream, expected_medians):
            mf_heap.add_num(num)
            mf_sort.add_num(num)
            assert mf_heap.find_median() == expected
            assert mf_sort.find_median() == expected
