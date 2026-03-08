"""Tests for LeetCode 167: Two Sum II."""

from p167_two_sum_ii import two_sum_ii


class TestTwoSumII:
    """Test the opposite-ends solution."""

    def test_basic(self):
        assert two_sum_ii([2, 7, 11, 15], 9) == [1, 2]

    def test_non_adjacent(self):
        assert two_sum_ii([2, 3, 4], 6) == [1, 3]

    def test_negative(self):
        assert two_sum_ii([-1, 0], -1) == [1, 2]

    def test_large_gap(self):
        assert two_sum_ii([1, 2, 3, 4, 5, 6, 7], 13) == [6, 7]

    def test_first_and_last(self):
        assert two_sum_ii([1, 10], 11) == [1, 2]

    def test_duplicates_in_array(self):
        assert two_sum_ii([1, 2, 2, 4], 4) == [2, 3]

    def test_negative_and_positive(self):
        assert two_sum_ii([-5, -3, 0, 2, 8], 5) == [2, 5]

    def test_target_zero(self):
        assert two_sum_ii([-3, -1, 0, 1, 5], 0) == [2, 4]
