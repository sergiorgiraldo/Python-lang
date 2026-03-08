"""Tests for LeetCode 75: Sort Colors."""

from p075_sort_colors import sort_colors, sort_colors_counting


class TestSortColors:
    """Test the Dutch National Flag solution."""

    def test_basic(self):
        nums = [2, 0, 2, 1, 1, 0]
        sort_colors(nums)
        assert nums == [0, 0, 1, 1, 2, 2]

    def test_three_elements(self):
        nums = [2, 0, 1]
        sort_colors(nums)
        assert nums == [0, 1, 2]

    def test_single(self):
        nums = [0]
        sort_colors(nums)
        assert nums == [0]

    def test_two_elements(self):
        nums = [1, 0]
        sort_colors(nums)
        assert nums == [0, 1]

    def test_already_sorted(self):
        nums = [0, 0, 1, 1, 2, 2]
        sort_colors(nums)
        assert nums == [0, 0, 1, 1, 2, 2]

    def test_reverse_sorted(self):
        nums = [2, 2, 1, 1, 0, 0]
        sort_colors(nums)
        assert nums == [0, 0, 1, 1, 2, 2]

    def test_all_zeros(self):
        nums = [0, 0, 0]
        sort_colors(nums)
        assert nums == [0, 0, 0]

    def test_all_twos(self):
        nums = [2, 2, 2]
        sort_colors(nums)
        assert nums == [2, 2, 2]

    def test_all_ones(self):
        nums = [1, 1, 1]
        sort_colors(nums)
        assert nums == [1, 1, 1]

    def test_no_ones(self):
        nums = [2, 0, 2, 0]
        sort_colors(nums)
        assert nums == [0, 0, 2, 2]

    def test_no_zeros(self):
        nums = [2, 1, 2, 1]
        sort_colors(nums)
        assert nums == [1, 1, 2, 2]


class TestSortColorsCounting:
    """Counting approach should produce same results."""

    def test_basic(self):
        nums = [2, 0, 2, 1, 1, 0]
        sort_colors_counting(nums)
        assert nums == [0, 0, 1, 1, 2, 2]

    def test_reverse(self):
        nums = [2, 2, 1, 1, 0, 0]
        sort_colors_counting(nums)
        assert nums == [0, 0, 1, 1, 2, 2]

    def test_single(self):
        nums = [1]
        sort_colors_counting(nums)
        assert nums == [1]
