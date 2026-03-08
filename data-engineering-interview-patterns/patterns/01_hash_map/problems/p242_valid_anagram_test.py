"""Tests for LeetCode 242: Valid Anagram."""

import pytest
from p242_valid_anagram import is_anagram, is_anagram_manual, is_anagram_sort


class TestIsAnagram:
    """Test the Counter-based solution."""

    def test_valid_anagram(self):
        assert is_anagram("anagram", "nagaram") is True

    def test_not_anagram(self):
        assert is_anagram("rat", "car") is False

    def test_empty_strings(self):
        assert is_anagram("", "") is True

    def test_different_lengths(self):
        assert is_anagram("a", "ab") is False

    def test_single_char_match(self):
        assert is_anagram("a", "a") is True

    def test_single_char_mismatch(self):
        assert is_anagram("a", "b") is False

    def test_repeated_chars(self):
        assert is_anagram("aacc", "ccac") is False

    def test_same_chars_different_freq(self):
        """Same character set but different frequencies."""
        assert is_anagram("aab", "abb") is False

    def test_unicode(self):
        """Works with non-ASCII characters."""
        assert is_anagram("café", "éfac") is True


class TestAllApproaches:
    """All approaches should produce identical results."""

    @pytest.mark.parametrize(
        "s, t, expected",
        [
            ("anagram", "nagaram", True),
            ("rat", "car", False),
            ("", "", True),
            ("a", "ab", False),
            ("aab", "abb", False),
        ],
    )
    def test_approaches_agree(self, s, t, expected):
        assert is_anagram(s, t) is expected
        assert is_anagram_manual(s, t) is expected
        assert is_anagram_sort(s, t) is expected
