"""Tests for LeetCode 895: Maximum Frequency Stack."""

from p895_max_freq_stack import FreqStack


class TestFreqStack:

    def test_example(self) -> None:
        fs = FreqStack()
        for val in [5, 7, 5, 7, 4, 5]:
            fs.push(val)

        assert fs.pop() == 5  # freq 3
        assert fs.pop() == 7  # freq 2 (most recent at freq 2)
        assert fs.pop() == 5  # freq 2
        assert fs.pop() == 4  # freq 1 (most recent at freq 1)

    def test_single_element(self) -> None:
        fs = FreqStack()
        fs.push(1)
        assert fs.pop() == 1

    def test_all_same(self) -> None:
        fs = FreqStack()
        fs.push(3)
        fs.push(3)
        fs.push(3)
        assert fs.pop() == 3
        assert fs.pop() == 3
        assert fs.pop() == 3

    def test_all_different(self) -> None:
        fs = FreqStack()
        fs.push(1)
        fs.push(2)
        fs.push(3)
        # All freq 1, pop most recent first (LIFO)
        assert fs.pop() == 3
        assert fs.pop() == 2
        assert fs.pop() == 1

    def test_push_after_pop(self) -> None:
        fs = FreqStack()
        fs.push(1)
        fs.push(1)
        assert fs.pop() == 1  # freq drops from 2 to 1
        fs.push(2)
        fs.push(2)
        assert fs.pop() == 2  # freq 2 most recent
        assert fs.pop() == 2  # freq 1 most recent
        assert fs.pop() == 1  # remaining

    def test_interleaved(self) -> None:
        fs = FreqStack()
        fs.push(10)
        fs.push(20)
        fs.push(10)
        assert fs.pop() == 10  # freq 2
        fs.push(20)
        assert fs.pop() == 20  # freq 2 (20 now has freq 2)
        assert fs.pop() == 20  # freq 1 most recent
        assert fs.pop() == 10  # freq 1
