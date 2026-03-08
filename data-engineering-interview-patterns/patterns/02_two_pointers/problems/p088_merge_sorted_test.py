"""Tests for LeetCode 88: Merge Sorted Array."""

from p088_merge_sorted import merge_new_array, merge_sorted_array


class TestMergeInPlace:
    """Test the in-place reverse-direction merge."""

    def test_basic(self):
        nums1 = [1, 2, 3, 0, 0, 0]
        merge_sorted_array(nums1, 3, [2, 5, 6], 3)
        assert nums1 == [1, 2, 2, 3, 5, 6]

    def test_nums2_empty(self):
        nums1 = [1]
        merge_sorted_array(nums1, 1, [], 0)
        assert nums1 == [1]

    def test_nums1_empty(self):
        nums1 = [0]
        merge_sorted_array(nums1, 0, [1], 1)
        assert nums1 == [1]

    def test_interleaved(self):
        nums1 = [1, 3, 5, 0, 0, 0]
        merge_sorted_array(nums1, 3, [2, 4, 6], 3)
        assert nums1 == [1, 2, 3, 4, 5, 6]

    def test_nums2_all_smaller(self):
        nums1 = [4, 5, 6, 0, 0, 0]
        merge_sorted_array(nums1, 3, [1, 2, 3], 3)
        assert nums1 == [1, 2, 3, 4, 5, 6]

    def test_nums2_all_larger(self):
        nums1 = [1, 2, 3, 0, 0, 0]
        merge_sorted_array(nums1, 3, [4, 5, 6], 3)
        assert nums1 == [1, 2, 3, 4, 5, 6]

    def test_duplicates(self):
        nums1 = [1, 2, 2, 0, 0]
        merge_sorted_array(nums1, 3, [2, 3], 2)
        assert nums1 == [1, 2, 2, 2, 3]

    def test_single_elements(self):
        nums1 = [2, 0]
        merge_sorted_array(nums1, 1, [1], 1)
        assert nums1 == [1, 2]


class TestMergeNewArray:
    """Test the simpler new-array version."""

    def test_basic(self):
        assert merge_new_array([1, 3, 5], [2, 4, 6]) == [1, 2, 3, 4, 5, 6]

    def test_empty_first(self):
        assert merge_new_array([], [1, 2]) == [1, 2]

    def test_empty_second(self):
        assert merge_new_array([1, 2], []) == [1, 2]

    def test_both_empty(self):
        assert merge_new_array([], []) == []

    def test_duplicates(self):
        assert merge_new_array([1, 3, 3], [2, 3, 4]) == [1, 2, 3, 3, 3, 4]
