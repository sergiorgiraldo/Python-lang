"""Tests for LeetCode 11: Container With Most Water."""

import pytest
from p011_container_water import max_area, max_area_brute


class TestMaxArea:
    """Test the opposite-ends greedy solution."""

    def test_basic(self):
        assert max_area([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49

    def test_two_elements(self):
        assert max_area([1, 1]) == 1

    def test_symmetric(self):
        assert max_area([4, 3, 2, 1, 4]) == 16

    def test_ascending(self):
        assert max_area([1, 2, 3, 4, 5]) == 6

    def test_descending(self):
        assert max_area([5, 4, 3, 2, 1]) == 6

    def test_all_same(self):
        assert max_area([5, 5, 5, 5]) == 15

    def test_single_tall(self):
        assert max_area([1, 1, 1, 100, 1, 1, 1]) == 6

    def test_tall_at_ends(self):
        assert max_area([10, 1, 1, 1, 10]) == 40


class TestBruteForceMatch:
    """Brute force should agree with optimal."""

    @pytest.mark.parametrize(
        "heights",
        [
            [1, 8, 6, 2, 5, 4, 8, 3, 7],
            [1, 1],
            [4, 3, 2, 1, 4],
            [1, 2, 3, 4, 5],
            [5, 5, 5, 5],
        ],
    )
    def test_matches_optimal(self, heights):
        assert max_area_brute(heights) == max_area(heights)
