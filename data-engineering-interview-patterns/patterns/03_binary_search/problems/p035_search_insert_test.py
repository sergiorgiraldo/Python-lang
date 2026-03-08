"""Tests for LeetCode 35: Search Insert Position."""

from p035_search_insert import search_insert


class TestSearchInsert:
    """Test the left-boundary binary search."""

    def test_found(self):
        assert search_insert([1, 3, 5, 6], 5) == 2

    def test_insert_middle(self):
        assert search_insert([1, 3, 5, 6], 2) == 1

    def test_insert_end(self):
        assert search_insert([1, 3, 5, 6], 7) == 4

    def test_insert_beginning(self):
        assert search_insert([1, 3, 5, 6], 0) == 0

    def test_single_found(self):
        assert search_insert([1], 1) == 0

    def test_single_insert_before(self):
        assert search_insert([1], 0) == 0

    def test_single_insert_after(self):
        assert search_insert([1], 2) == 1

    def test_first_element(self):
        assert search_insert([1, 3, 5], 1) == 0

    def test_last_element(self):
        assert search_insert([1, 3, 5], 5) == 2

    def test_between_every_pair(self):
        """Target falls between each consecutive pair."""
        arr = [10, 20, 30, 40, 50]
        assert search_insert(arr, 15) == 1
        assert search_insert(arr, 25) == 2
        assert search_insert(arr, 35) == 3
        assert search_insert(arr, 45) == 4
