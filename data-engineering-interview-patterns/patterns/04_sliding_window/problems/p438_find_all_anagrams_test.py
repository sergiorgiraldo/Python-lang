"""Tests for LeetCode 438: Find All Anagrams in a String."""

import pytest
from p438_find_all_anagrams import find_anagrams, find_anagrams_counter


class TestFindAnagrams:
    """Test the frequency-match sliding window."""

    def test_basic(self):
        assert find_anagrams("cbaebabacd", "abc") == [0, 6]

    def test_overlapping(self):
        assert find_anagrams("abab", "ab") == [0, 1, 2]

    def test_pattern_longer(self):
        assert find_anagrams("a", "ab") == []

    def test_no_match(self):
        assert find_anagrams("xyz", "abc") == []

    def test_exact_match(self):
        assert find_anagrams("abc", "abc") == [0]

    def test_single_char(self):
        assert find_anagrams("aaaa", "a") == [0, 1, 2, 3]

    def test_repeated_pattern(self):
        assert find_anagrams("aababaa", "aab") == [0, 1, 3, 4]

    def test_all_same(self):
        assert find_anagrams("aaa", "aa") == [0, 1]

    def test_empty_text(self):
        assert find_anagrams("", "a") == []

    def test_match_at_end(self):
        assert find_anagrams("xyzabc", "cab") == [3]


class TestCounterApproachMatch:
    """Counter comparison should match frequency-match approach."""

    @pytest.mark.parametrize(
        "s,p",
        [
            ("cbaebabacd", "abc"),
            ("abab", "ab"),
            ("a", "ab"),
            ("xyz", "abc"),
            ("aaaa", "a"),
            ("aababaa", "aab"),
        ],
    )
    def test_matches_optimal(self, s, p):
        assert find_anagrams_counter(s, p) == find_anagrams(s, p)
