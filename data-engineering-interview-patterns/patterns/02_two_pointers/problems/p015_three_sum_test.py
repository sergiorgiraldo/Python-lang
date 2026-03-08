"""Tests for LeetCode 15: 3Sum."""

from p015_three_sum import three_sum


class TestThreeSum:
    """Test the sort + two pointers solution."""

    def test_basic(self):
        result = three_sum([-1, 0, 1, 2, -1, -4])
        assert result == [[-1, -1, 2], [-1, 0, 1]]

    def test_no_solution(self):
        assert three_sum([0, 1, 1]) == []

    def test_all_zeros(self):
        assert three_sum([0, 0, 0]) == [[0, 0, 0]]

    def test_empty(self):
        assert three_sum([]) == []

    def test_two_elements(self):
        assert three_sum([1, -1]) == []

    def test_multiple_triplets(self):
        result = three_sum([-2, -1, 0, 1, 2, 3])
        assert [-2, -1, 3] in result
        assert [-2, 0, 2] in result
        assert [-1, 0, 1] in result

    def test_all_negative(self):
        assert three_sum([-3, -2, -1]) == []

    def test_all_positive(self):
        assert three_sum([1, 2, 3]) == []

    def test_duplicates_handled(self):
        """Multiple identical values shouldn't produce duplicate triplets."""
        result = three_sum([-1, -1, -1, 0, 1, 1, 1])
        assert result == [[-1, 0, 1]]

    def test_large_duplicates(self):
        """Stress test duplicate skipping."""
        result = three_sum([0, 0, 0, 0, 0])
        assert result == [[0, 0, 0]]
