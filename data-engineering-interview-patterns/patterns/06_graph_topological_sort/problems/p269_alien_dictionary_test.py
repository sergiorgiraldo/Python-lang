"""Tests for LeetCode 269: Alien Dictionary."""

import pytest
from p269_alien_dictionary import alien_order, alien_order_dfs


def is_valid_alien_order(result: str, words: list[str]) -> bool:
    """Verify that the result is consistent with the word ordering."""
    if not result:
        return True
    char_rank = {c: i for i, c in enumerate(result)}
    all_chars = {c for word in words for c in word}
    if set(result) != all_chars:
        return False
    for i in range(len(words) - 1):
        w1, w2 = words[i], words[i + 1]
        for j in range(min(len(w1), len(w2))):
            if w1[j] != w2[j]:
                if char_rank[w1[j]] >= char_rank[w2[j]]:
                    return False
                break
        else:
            if len(w1) > len(w2):
                return False
    return True


class TestAlienOrder:
    @pytest.mark.parametrize("fn", [alien_order, alien_order_dfs])
    def test_example(self, fn):
        result = fn(["wrt", "wrf", "er", "ett", "rftt"])
        assert is_valid_alien_order(result, ["wrt", "wrf", "er", "ett", "rftt"])

    @pytest.mark.parametrize("fn", [alien_order, alien_order_dfs])
    def test_simple(self, fn):
        result = fn(["z", "x"])
        assert is_valid_alien_order(result, ["z", "x"])

    @pytest.mark.parametrize("fn", [alien_order, alien_order_dfs])
    def test_cycle(self, fn):
        assert fn(["z", "x", "z"]) == ""

    @pytest.mark.parametrize("fn", [alien_order, alien_order_dfs])
    def test_single_word(self, fn):
        result = fn(["abc"])
        assert set(result) == {"a", "b", "c"}

    @pytest.mark.parametrize("fn", [alien_order, alien_order_dfs])
    def test_single_char_words(self, fn):
        result = fn(["z", "z"])
        assert result == "z"

    @pytest.mark.parametrize("fn", [alien_order, alien_order_dfs])
    def test_prefix_invalid(self, fn):
        assert fn(["abc", "ab"]) == ""

    @pytest.mark.parametrize("fn", [alien_order, alien_order_dfs])
    def test_prefix_valid(self, fn):
        result = fn(["ab", "abc"])
        assert set(result) == {"a", "b", "c"}

    @pytest.mark.parametrize("fn", [alien_order, alien_order_dfs])
    def test_all_same(self, fn):
        result = fn(["a", "a", "a"])
        assert result == "a"

    @pytest.mark.parametrize("fn", [alien_order, alien_order_dfs])
    def test_three_chars(self, fn):
        result = fn(["abc", "bcd"])
        assert is_valid_alien_order(result, ["abc", "bcd"])
