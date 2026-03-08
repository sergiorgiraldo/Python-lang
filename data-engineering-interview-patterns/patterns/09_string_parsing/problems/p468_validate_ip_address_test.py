"""Tests for LeetCode 468: Validate IP Address."""

import pytest

from p468_validate_ip_address import valid_ip_address


class TestValidIPAddress:
    """Core IP validation tests."""

    # IPv4 valid
    def test_ipv4_basic(self) -> None:
        assert valid_ip_address("172.16.254.1") == "IPv4"

    def test_ipv4_zeros(self) -> None:
        assert valid_ip_address("0.0.0.0") == "IPv4"

    def test_ipv4_max(self) -> None:
        assert valid_ip_address("255.255.255.255") == "IPv4"

    # IPv4 invalid
    def test_ipv4_leading_zero(self) -> None:
        assert valid_ip_address("172.16.254.01") == "Neither"

    def test_ipv4_too_large(self) -> None:
        assert valid_ip_address("256.256.256.256") == "Neither"

    def test_ipv4_too_few_parts(self) -> None:
        assert valid_ip_address("1.2.3") == "Neither"

    def test_ipv4_too_many_parts(self) -> None:
        assert valid_ip_address("1.2.3.4.5") == "Neither"

    def test_ipv4_empty_segment(self) -> None:
        assert valid_ip_address("1..3.4") == "Neither"

    def test_ipv4_non_numeric(self) -> None:
        assert valid_ip_address("1.2.3.a") == "Neither"

    def test_ipv4_negative(self) -> None:
        assert valid_ip_address("1.2.3.-1") == "Neither"

    # IPv6 valid
    def test_ipv6_basic(self) -> None:
        assert valid_ip_address("2001:0db8:85a3:0000:0000:8a2e:0370:7334") == "IPv6"

    def test_ipv6_short_groups(self) -> None:
        assert valid_ip_address("2001:db8:85a3:0:0:8A2E:370:7334") == "IPv6"

    def test_ipv6_mixed_case(self) -> None:
        assert valid_ip_address("2001:0db8:85a3:0:0:8a2E:0370:7334") == "IPv6"

    # IPv6 invalid
    def test_ipv6_too_few_groups(self) -> None:
        assert valid_ip_address("2001:0db8:85a3:0:0:8a2e:0370") == "Neither"

    def test_ipv6_too_long_group(self) -> None:
        assert valid_ip_address("2001:0db8:85a3:00000:0:8a2e:0370:7334") == "Neither"

    def test_ipv6_non_hex(self) -> None:
        assert valid_ip_address("2001:0db8:85a3:0:0:8a2g:0370:7334") == "Neither"

    def test_ipv6_empty_group(self) -> None:
        assert valid_ip_address("2001:0db8:85a3::0:8a2e:0370:7334") == "Neither"

    # Edge cases
    def test_empty_string(self) -> None:
        assert valid_ip_address("") == "Neither"

    def test_neither(self) -> None:
        assert valid_ip_address("hello") == "Neither"

    def test_trailing_dot(self) -> None:
        assert valid_ip_address("1.2.3.4.") == "Neither"
