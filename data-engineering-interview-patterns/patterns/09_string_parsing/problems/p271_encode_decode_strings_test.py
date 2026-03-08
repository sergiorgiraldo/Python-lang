"""Tests for LeetCode 271: Encode and Decode Strings."""

import pytest

from p271_encode_decode_strings import (
    decode,
    decode_escaped,
    encode,
    encode_escaped,
)


@pytest.mark.parametrize(
    "enc,dec",
    [(encode, decode), (encode_escaped, decode_escaped)],
)
class TestEncodeDecode:
    """Test both encoding approaches."""

    def test_basic(self, enc, dec) -> None:
        strs = ["hello", "world"]
        assert dec(enc(strs)) == strs

    def test_empty_strings(self, enc, dec) -> None:
        strs = ["", ""]
        assert dec(enc(strs)) == strs

    def test_empty_list(self, enc, dec) -> None:
        strs: list[str] = []
        assert dec(enc(strs)) == strs

    def test_special_characters(self, enc, dec) -> None:
        strs = ["hello#world", "foo#bar"]
        assert dec(enc(strs)) == strs

    def test_delimiter_in_content(self, enc, dec) -> None:
        strs = ["a,b,c", "d,e"]
        assert dec(enc(strs)) == strs

    def test_numbers_in_content(self, enc, dec) -> None:
        strs = ["123", "456#789"]
        assert dec(enc(strs)) == strs

    def test_single_string(self, enc, dec) -> None:
        strs = ["only one"]
        assert dec(enc(strs)) == strs

    def test_long_strings(self, enc, dec) -> None:
        strs = ["a" * 1000, "b" * 500]
        assert dec(enc(strs)) == strs

    def test_mixed_empty_and_content(self, enc, dec) -> None:
        strs = ["", "hello", "", "world", ""]
        assert dec(enc(strs)) == strs

    def test_unicode(self, enc, dec) -> None:
        strs = ["cafe\u0301", "nai\u0308ve", "\u65e5\u672c\u8a9e"]
        assert dec(enc(strs)) == strs

    def test_newlines(self, enc, dec) -> None:
        strs = ["line1\nline2", "line3"]
        assert dec(enc(strs)) == strs
