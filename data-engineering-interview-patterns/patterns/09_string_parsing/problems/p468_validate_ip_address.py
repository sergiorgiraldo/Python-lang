"""
LeetCode 468: Validate IP Address

Pattern: String Parsing - Structured validation with rules
Difficulty: Medium
Time Complexity: O(n) where n is string length
Space Complexity: O(1) extra
"""


def valid_ip_address(query_ip: str) -> str:
    """
    Determine if a string is a valid IPv4, IPv6 or Neither.

    IPv4: 4 groups of 0-255, separated by '.', no leading zeros (except "0").
    IPv6: 8 groups of 1-4 hex digits, separated by ':', leading zeros allowed.
    """
    if "." in query_ip:
        return "IPv4" if _is_valid_ipv4(query_ip) else "Neither"
    elif ":" in query_ip:
        return "IPv6" if _is_valid_ipv6(query_ip) else "Neither"
    return "Neither"


def _is_valid_ipv4(ip: str) -> bool:
    """Validate IPv4 address."""
    parts = ip.split(".")
    if len(parts) != 4:
        return False

    for part in parts:
        if not part:  # empty segment (e.g., "1..2.3")
            return False
        if not part.isdigit():  # non-numeric (handles negative too)
            return False
        if len(part) > 1 and part[0] == "0":  # leading zero
            return False
        if int(part) > 255:
            return False

    return True


def _is_valid_ipv6(ip: str) -> bool:
    """Validate IPv6 address."""
    parts = ip.split(":")
    if len(parts) != 8:
        return False

    hex_chars = set("0123456789abcdefABCDEF")

    for part in parts:
        if not part or len(part) > 4:  # empty or too long
            return False
        if not all(c in hex_chars for c in part):  # non-hex character
            return False

    return True
