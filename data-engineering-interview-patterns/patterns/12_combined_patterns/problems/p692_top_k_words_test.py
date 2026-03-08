"""Tests for LeetCode 692: Top K Frequent Words."""

import pytest

from p692_top_k_words import top_k_frequent, top_k_frequent_sort


@pytest.mark.parametrize("func", [top_k_frequent, top_k_frequent_sort])
class TestTopKWords:

    def test_example_1(self, func) -> None:
        words = ["i", "love", "leetcode", "i", "love", "coding"]
        assert func(words, 2) == ["i", "love"]

    def test_example_2(self, func) -> None:
        words = ["the", "day", "is", "sunny", "the", "the", "the",
                 "sunny", "is", "is"]
        assert func(words, 4) == ["the", "is", "sunny", "day"]

    def test_single_word(self, func) -> None:
        assert func(["hello"], 1) == ["hello"]

    def test_all_same_frequency(self, func) -> None:
        # All appear once, sort lexicographically
        result = func(["b", "a", "c"], 2)
        assert result == ["a", "b"]

    def test_k_equals_unique(self, func) -> None:
        words = ["a", "b", "b"]
        assert func(words, 2) == ["b", "a"]

    def test_tiebreaker(self, func) -> None:
        # "apple" and "banana" both appear twice
        words = ["banana", "apple", "banana", "apple", "cherry"]
        result = func(words, 2)
        assert result == ["apple", "banana"]  # lex order for ties
