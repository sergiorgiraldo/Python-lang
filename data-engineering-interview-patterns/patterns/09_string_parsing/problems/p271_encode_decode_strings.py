"""
LeetCode 271: Encode and Decode Strings

Pattern: String Parsing - Serialization with length prefixing
Difficulty: Medium
Time Complexity: O(n) where n is total characters across all strings
Space Complexity: O(n) for the encoded string
"""


def encode(strs: list[str]) -> str:
    """
    Encode a list of strings into a single string.

    Uses length-prefix encoding: each string is preceded by its
    length and a delimiter. "hello" becomes "5#hello".

    This handles any content in the strings (including the delimiter
    character) because we know exactly how many characters to read.
    """
    parts: list[str] = []
    for s in strs:
        parts.append(f"{len(s)}#{s}")
    return "".join(parts)


def decode(s: str) -> list[str]:
    """
    Decode a single string back into a list of strings.

    Read the length (digits before #), then read exactly that
    many characters. The length prefix makes this unambiguous
    regardless of what characters appear in the original strings.
    """
    result: list[str] = []
    i = 0

    while i < len(s):
        # Find the # delimiter
        j = i
        while s[j] != "#":
            j += 1

        length = int(s[i:j])
        # Read exactly 'length' characters after the #
        result.append(s[j + 1 : j + 1 + length])
        i = j + 1 + length

    return result


def encode_escaped(strs: list[str]) -> str:
    """
    Alternative: escape-based encoding.

    Escape any occurrence of the delimiter in the content.
    Simpler concept but more error-prone with edge cases.
    """
    escaped = []
    for s in strs:
        escaped.append(s.replace("/", "//").replace(",", "/,"))
    return ",".join(escaped)


def decode_escaped(s: str) -> list[str]:
    """Decode escape-based encoding."""
    if s == "":
        return []

    result: list[str] = []
    current: list[str] = []
    i = 0

    while i < len(s):
        if s[i] == "/" and i + 1 < len(s):
            current.append(s[i + 1])
            i += 2
        elif s[i] == ",":
            result.append("".join(current))
            current = []
            i += 1
        else:
            current.append(s[i])
            i += 1

    result.append("".join(current))
    return result
