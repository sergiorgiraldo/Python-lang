"""Tests for LeetCode 26: Remove Duplicates from Sorted Array."""

from p026_remove_duplicates import remove_duplicates


class TestRemoveDuplicates:
    """Test the read/write pointer solution."""

    def test_basic(self):
        nums = [1, 1, 2]
        assert remove_duplicates(nums) == 2
        assert nums[:2] == [1, 2]

    def test_longer(self):
        nums = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]
        assert remove_duplicates(nums) == 5
        assert nums[:5] == [0, 1, 2, 3, 4]

    def test_empty(self):
        nums: list[int] = []
        assert remove_duplicates(nums) == 0

    def test_single(self):
        nums = [1]
        assert remove_duplicates(nums) == 1
        assert nums[:1] == [1]

    def test_no_duplicates(self):
        nums = [1, 2, 3, 4, 5]
        assert remove_duplicates(nums) == 5
        assert nums == [1, 2, 3, 4, 5]

    def test_all_same(self):
        nums = [7, 7, 7, 7]
        assert remove_duplicates(nums) == 1
        assert nums[0] == 7

    def test_two_elements_same(self):
        nums = [1, 1]
        assert remove_duplicates(nums) == 1

    def test_two_elements_different(self):
        nums = [1, 2]
        assert remove_duplicates(nums) == 2
        assert nums[:2] == [1, 2]

    def test_negative_numbers(self):
        nums = [-3, -1, -1, 0, 0, 2]
        assert remove_duplicates(nums) == 4
        assert nums[:4] == [-3, -1, 0, 2]
