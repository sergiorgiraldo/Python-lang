"""Tests for LeetCode 49: Group Anagrams."""

import pytest
from p049_group_anagrams import group_anagrams, group_anagrams_count


def normalize_groups(groups: list[list[str]]) -> list[list[str]]:
    """Sort each group and sort the list of groups for comparison."""
    return sorted([sorted(g) for g in groups])


class TestGroupAnagrams:
    """Test the sort-based grouping solution."""

    def test_basic_case(self):
        result = group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
        expected = [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]]
        assert normalize_groups(result) == expected

    def test_single_string(self):
        result = group_anagrams(["a"])
        assert normalize_groups(result) == [["a"]]

    def test_empty_strings(self):
        result = group_anagrams([""])
        assert normalize_groups(result) == [[""]]

    def test_all_same(self):
        result = group_anagrams(["a", "a", "a"])
        assert normalize_groups(result) == [["a", "a", "a"]]

    def test_no_anagrams(self):
        result = group_anagrams(["abc", "def", "ghi"])
        expected = [["abc"], ["def"], ["ghi"]]
        assert normalize_groups(result) == expected

    def test_empty_input(self):
        result = group_anagrams([])
        assert result == []

    def test_mixed_lengths(self):
        result = group_anagrams(["a", "ab", "ba", "abc"])
        expected = [["a"], ["ab", "ba"], ["abc"]]
        assert normalize_groups(result) == expected


class TestGroupAnagramsCount:
    """Test the frequency-count approach and verify it matches."""

    @pytest.mark.parametrize(
        "strs",
        [
            ["eat", "tea", "tan", "ate", "nat", "bat"],
            ["a"],
            [""],
            ["abc", "def", "ghi"],
            ["a", "ab", "ba", "abc"],
        ],
    )
    def test_matches_sort_approach(self, strs):
        result_sort = normalize_groups(group_anagrams(strs))
        result_count = normalize_groups(group_anagrams_count(strs))
        assert result_sort == result_count
