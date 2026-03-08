"""Tests for LeetCode 162: Find Peak Element."""

from p162_find_peak import find_peak_element, find_peak_linear


def is_peak(nums: list[int], idx: int) -> bool:
    """Verify that idx is actually a peak in nums."""
    if idx < 0 or idx >= len(nums):
        return False
    left_ok = idx == 0 or nums[idx] > nums[idx - 1]
    right_ok = idx == len(nums) - 1 or nums[idx] > nums[idx + 1]
    return left_ok and right_ok


class TestFindPeakElement:
    """Test binary search for peak element."""

    def test_single_peak(self):
        result = find_peak_element([1, 2, 3, 1])
        assert is_peak([1, 2, 3, 1], result)

    def test_multiple_peaks(self):
        """Any valid peak is acceptable."""
        nums = [1, 2, 1, 3, 5, 6, 4]
        result = find_peak_element(nums)
        assert is_peak(nums, result)

    def test_single_element(self):
        assert find_peak_element([1]) == 0

    def test_two_ascending(self):
        result = find_peak_element([1, 2])
        assert is_peak([1, 2], result)

    def test_two_descending(self):
        result = find_peak_element([2, 1])
        assert is_peak([2, 1], result)

    def test_ascending_array(self):
        """Peak is the last element (boundary is -inf)."""
        nums = [1, 2, 3, 4, 5]
        result = find_peak_element(nums)
        assert is_peak(nums, result)

    def test_descending_array(self):
        """Peak is the first element."""
        nums = [5, 4, 3, 2, 1]
        result = find_peak_element(nums)
        assert is_peak(nums, result)

    def test_valley_shape(self):
        """Peak is at either end."""
        nums = [5, 1, 5]
        result = find_peak_element(nums)
        assert is_peak(nums, result)

    def test_mountain_shape(self):
        nums = [1, 3, 5, 4, 2]
        result = find_peak_element(nums)
        assert is_peak(nums, result)

    def test_zigzag(self):
        """Multiple peaks in zigzag pattern."""
        nums = [1, 3, 2, 4, 1]
        result = find_peak_element(nums)
        assert is_peak(nums, result)


class TestLinearMatch:
    """Linear approach should also find valid peaks."""

    def test_single_peak(self):
        nums = [1, 2, 3, 1]
        result = find_peak_linear(nums)
        assert is_peak(nums, result)

    def test_ascending(self):
        nums = [1, 2, 3, 4, 5]
        result = find_peak_linear(nums)
        assert is_peak(nums, result)

    def test_multiple_peaks(self):
        nums = [1, 3, 2, 4, 1]
        result = find_peak_linear(nums)
        assert is_peak(nums, result)
