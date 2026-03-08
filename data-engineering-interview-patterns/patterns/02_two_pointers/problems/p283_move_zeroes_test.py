"""Tests for LeetCode 283: Move Zeroes."""

from p283_move_zeroes import move_zeroes, move_zeroes_swap


class TestMoveZeroes:
    """Test the overwrite-then-zero approach."""

    def test_basic(self):
        nums = [0, 1, 0, 3, 12]
        move_zeroes(nums)
        assert nums == [1, 3, 12, 0, 0]

    def test_single_zero(self):
        nums = [0]
        move_zeroes(nums)
        assert nums == [0]

    def test_no_zeroes(self):
        nums = [1, 2, 3]
        move_zeroes(nums)
        assert nums == [1, 2, 3]

    def test_all_zeroes(self):
        nums = [0, 0, 0]
        move_zeroes(nums)
        assert nums == [0, 0, 0]

    def test_zeroes_at_end(self):
        """Already in correct position."""
        nums = [1, 2, 0, 0]
        move_zeroes(nums)
        assert nums == [1, 2, 0, 0]

    def test_zeroes_at_start(self):
        nums = [0, 0, 1, 2]
        move_zeroes(nums)
        assert nums == [1, 2, 0, 0]

    def test_alternating(self):
        nums = [0, 1, 0, 2, 0, 3]
        move_zeroes(nums)
        assert nums == [1, 2, 3, 0, 0, 0]

    def test_single_nonzero(self):
        nums = [1]
        move_zeroes(nums)
        assert nums == [1]


class TestMoveZeroesSwap:
    """Swap variant should produce same results."""

    def test_basic(self):
        nums = [0, 1, 0, 3, 12]
        move_zeroes_swap(nums)
        assert nums == [1, 3, 12, 0, 0]

    def test_all_zeroes(self):
        nums = [0, 0, 0]
        move_zeroes_swap(nums)
        assert nums == [0, 0, 0]

    def test_no_zeroes(self):
        nums = [1, 2, 3]
        move_zeroes_swap(nums)
        assert nums == [1, 2, 3]

    def test_alternating(self):
        nums = [0, 1, 0, 2, 0, 3]
        move_zeroes_swap(nums)
        assert nums == [1, 2, 3, 0, 0, 0]
