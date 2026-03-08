"""Tests for LeetCode 875: Koko Eating Bananas."""

import pytest
from p875_koko_bananas import min_eating_speed, min_eating_speed_brute


class TestMinEatingSpeed:
    """Test binary search on answer for eating speed."""

    def test_basic(self):
        assert min_eating_speed([3, 6, 7, 11], 8) == 4

    def test_tight_deadline(self):
        """h equals number of piles - must eat max pile in one hour."""
        assert min_eating_speed([30, 11, 23, 4, 20], 5) == 30

    def test_relaxed_deadline(self):
        assert min_eating_speed([30, 11, 23, 4, 20], 6) == 23

    def test_single_pile(self):
        assert min_eating_speed([1], 1) == 1

    def test_single_large_pile(self):
        """One pile, multiple hours."""
        assert min_eating_speed([100], 10) == 10

    def test_equal_piles(self):
        assert min_eating_speed([5, 5, 5, 5], 4) == 5
        assert min_eating_speed([5, 5, 5, 5], 8) == 3

    def test_h_much_larger(self):
        """Plenty of time - can eat very slowly."""
        assert min_eating_speed([3, 6, 7, 11], 100) == 1

    def test_one_banana_piles(self):
        assert min_eating_speed([1, 1, 1], 3) == 1


class TestBruteForceMatch:
    """Brute force should agree with binary search."""

    @pytest.mark.parametrize(
        "piles,h",
        [
            ([3, 6, 7, 11], 8),
            ([30, 11, 23, 4, 20], 5),
            ([30, 11, 23, 4, 20], 6),
            ([1], 1),
            ([100], 10),
            ([5, 5, 5, 5], 8),
        ],
    )
    def test_matches_binary(self, piles, h):
        assert min_eating_speed_brute(piles, h) == min_eating_speed(piles, h)
