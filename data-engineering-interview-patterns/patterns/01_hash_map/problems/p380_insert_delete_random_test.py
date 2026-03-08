"""Tests for LeetCode 380: Insert Delete GetRandom O(1)."""

from p380_insert_delete_random import RandomizedSet


class TestRandomizedSet:
    """Test insert, remove and getRandom operations."""

    def test_insert_new(self):
        rs = RandomizedSet()
        assert rs.insert(1) is True

    def test_insert_duplicate(self):
        rs = RandomizedSet()
        rs.insert(1)
        assert rs.insert(1) is False

    def test_remove_existing(self):
        rs = RandomizedSet()
        rs.insert(1)
        assert rs.remove(1) is True

    def test_remove_nonexistent(self):
        rs = RandomizedSet()
        assert rs.remove(1) is False

    def test_get_random_single(self):
        rs = RandomizedSet()
        rs.insert(42)
        assert rs.get_random() == 42

    def test_get_random_returns_existing(self):
        """Random element must be one that was inserted."""
        rs = RandomizedSet()
        inserted = {1, 2, 3, 4, 5}
        for val in inserted:
            rs.insert(val)
        for _ in range(50):
            assert rs.get_random() in inserted

    def test_remove_then_random(self):
        """Removed elements should never appear in getRandom."""
        rs = RandomizedSet()
        rs.insert(1)
        rs.insert(2)
        rs.insert(3)
        rs.remove(2)
        for _ in range(50):
            assert rs.get_random() in {1, 3}

    def test_insert_remove_insert(self):
        """Re-inserting a removed value should work."""
        rs = RandomizedSet()
        rs.insert(1)
        rs.remove(1)
        assert rs.insert(1) is True

    def test_leetcode_example(self):
        """Match the LeetCode example sequence."""
        rs = RandomizedSet()
        assert rs.insert(1) is True
        assert rs.remove(2) is False
        assert rs.insert(2) is True
        assert rs.get_random() in {1, 2}
        assert rs.remove(1) is True
        assert rs.insert(2) is False
        assert rs.get_random() == 2

    def test_swap_correctness(self):
        """Verify the swap-with-last logic works for middle elements."""
        rs = RandomizedSet()
        for val in [10, 20, 30, 40, 50]:
            rs.insert(val)
        rs.remove(30)  # should swap 30 with 50, then pop
        assert 30 not in rs.val_to_index
        assert len(rs.values) == 4
        # All remaining values should be findable
        for val in [10, 20, 40, 50]:
            assert val in rs.val_to_index

    def test_remove_last_element(self):
        """Removing the last element in the list is a special case of the swap."""
        rs = RandomizedSet()
        rs.insert(1)
        rs.insert(2)
        rs.remove(2)  # 2 is already the last element
        assert rs.values == [1]
        assert rs.val_to_index == {1: 0}
