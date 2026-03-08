"""Tests for LeetCode 153: Find Minimum in Rotated Sorted Array."""

import pytest
from p153_find_min_rotated import find_min, find_min_linear


class TestFindMin:
    """Test binary search for minimum in rotated array."""

    def test_rotated_middle(self):
        assert find_min([3, 4, 5, 1, 2]) == 1

    def test_rotated_late(self):
        assert find_min([4, 5, 6, 7, 0, 1, 2]) == 0

    def test_not_rotated(self):
        """Array rotated by 0 (or n) - already sorted."""
        assert find_min([11, 13, 15, 17]) == 11

    def test_two_elements_rotated(self):
        assert find_min([2, 1]) == 1

    def test_two_elements_sorted(self):
        assert find_min([1, 2]) == 1

    def test_single_element(self):
        assert find_min([1]) == 1

    def test_rotation_at_end(self):
        """Last element is smallest - rotated by 1."""
        assert find_min([2, 3, 4, 5, 1]) == 1

    def test_rotation_at_start(self):
        """First element is smallest - rotated by n-1."""
        assert find_min([1, 2, 3, 4, 5]) == 1

    def test_all_rotations(self):
        """Test every possible rotation of [1,2,3,4,5]."""
        base = [1, 2, 3, 4, 5]
        for i in range(len(base)):
            rotated = base[i:] + base[:i]
            assert find_min(rotated) == 1, f"Failed on rotation {rotated}"

    def test_large_values(self):
        assert find_min([100, 200, 300, 1, 50]) == 1


class TestLinearMatch:
    """Linear scan should agree with binary search."""

    @pytest.mark.parametrize(
        "nums",
        [
            [3, 4, 5, 1, 2],
            [4, 5, 6, 7, 0, 1, 2],
            [11, 13, 15, 17],
            [2, 1],
            [1],
        ],
    )
    def test_matches_binary(self, nums):
        assert find_min_linear(nums) == find_min(nums)
