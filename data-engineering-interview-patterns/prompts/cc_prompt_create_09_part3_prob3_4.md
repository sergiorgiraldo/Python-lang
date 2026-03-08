# CC Prompt: Create Pattern 09 String Parsing (Part 3 of 5)

## What This Prompt Does

Creates problems 3-4: Remove Comments (LeetCode 722) and Validate IP Address (LeetCode 468).

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Every .md Worked Example starts with a prose paragraph
- Every approach explanation teaches the "why" not just the "what"

---

## Problem 3: Remove Comments (LeetCode #722)

### `problems/p722_remove_comments.py`

```python
"""
LeetCode 722: Remove Comments

Pattern: String Parsing - State machine
Difficulty: Medium
Time Complexity: O(n) where n is total characters
Space Complexity: O(n) for the output
"""


def remove_comments(source: list[str]) -> list[str]:
    """
    Remove C-style comments from source code.

    Two types of comments:
    - Line comment "//": ignore everything from // to end of line
    - Block comment "/* ... */": ignore everything between, can span lines

    Uses a state machine with two states:
    - in_block=False: normal mode, output characters
    - in_block=True: inside a block comment, skip characters

    Process character by character, looking ahead one character
    for "//" and "/*" and "*/" sequences.
    """
    result: list[str] = []
    current_line: list[str] = []
    in_block = False

    for line in source:
        i = 0
        while i < len(line):
            if in_block:
                # Looking for end of block comment
                if i + 1 < len(line) and line[i : i + 2] == "*/":
                    in_block = False
                    i += 2
                else:
                    i += 1
            else:
                if i + 1 < len(line) and line[i : i + 2] == "//":
                    # Line comment: skip rest of line
                    break
                elif i + 1 < len(line) and line[i : i + 2] == "/*":
                    # Block comment: enter block state
                    in_block = True
                    i += 2
                else:
                    current_line.append(line[i])
                    i += 1

        # Only add the line if we're not in a block comment
        # and the line has content
        if not in_block and current_line:
            result.append("".join(current_line))
            current_line = []

    return result
```

### `problems/p722_remove_comments_test.py`

```python
"""Tests for LeetCode 722: Remove Comments."""

import pytest

from .p722_remove_comments import remove_comments


class TestRemoveComments:
    """Core comment removal tests."""

    def test_line_comments(self) -> None:
        source = [
            "int x = 1; // initialize x",
            "int y = 2; // initialize y",
        ]
        assert remove_comments(source) == ["int x = 1; ", "int y = 2; "]

    def test_block_comment_single_line(self) -> None:
        source = ["int x = 1; /* comment */ int y = 2;"]
        assert remove_comments(source) == ["int x = 1;  int y = 2;"]

    def test_block_comment_multiline(self) -> None:
        source = [
            "int x = 1;",
            "/* this is a",
            "   multiline comment */",
            "int y = 2;",
        ]
        assert remove_comments(source) == ["int x = 1;", "int y = 2;"]

    def test_block_removes_lines(self) -> None:
        source = [
            "a",
            "/*",
            "b",
            "*/",
            "c",
        ]
        assert remove_comments(source) == ["a", "c"]

    def test_mixed_comments(self) -> None:
        source = [
            "// full line comment",
            "int x = 1;",
            "/* block */ int y = 2;",
        ]
        assert remove_comments(source) == ["int x = 1;", " int y = 2;"]

    def test_block_comment_joins_lines(self) -> None:
        source = [
            "a /* block",
            "comment */ b",
        ]
        assert remove_comments(source) == ["a  b"]

    def test_no_comments(self) -> None:
        source = ["int x = 1;", "int y = 2;"]
        assert remove_comments(source) == ["int x = 1;", "int y = 2;"]

    def test_empty_input(self) -> None:
        assert remove_comments([]) == []

    def test_leetcode_example(self) -> None:
        source = [
            "/*Test program */",
            "int main()",
            "{ ",
            "  // variable declaration ",
            "int a, b, c;",
            "/* This is a test",
            "   multiline  ",
            "   comment for ",
            "   testing */",
            "a = b + c;",
            "}",
        ]
        expected = ["int main()", "{ ", "  ", "int a, b, c;", "a = b + c;", "}"]
        assert remove_comments(source) == expected
```

### `problems/722_remove_comments.md`

````markdown
# Remove Comments (LeetCode #722)

## Problem Statement

Given a C++ program as a list of source code lines, remove all comments. Line comments (`//`) extend to the end of the line. Block comments (`/* ... */`) can span multiple lines. Return the remaining code as a list of strings (skip empty lines).

## Thought Process

1. **State machine:** At any point in the code, we're in one of two states: normal (output characters) or inside a block comment (skip characters). Line comments are simpler - just stop processing the current line.
2. **Look-ahead:** We need to check two characters at a time to detect `//`, `/*` and `*/`. Single-character scanning isn't enough.
3. **Line joining:** When a block comment spans multiple lines, the text before and after the comment might merge into one line. This is the trickiest edge case.

## Worked Example

The state machine has two states: normal and in-block-comment. In normal state, we output characters and watch for comment starts. In block-comment state, we skip everything and watch for the block end. Line comments are handled in normal state by breaking out of the current line.

```
Source:
  Line 0: "a /* block"
  Line 1: "comment */ b"

Processing:
  Line 0, normal state:
    'a'  → output 'a'. current_line = ['a']
    ' '  → output ' '. current_line = ['a', ' ']
    '/'  → peek ahead: '/*' → enter block comment. i += 2.
    'b','l','o','c','k' → skipped (in_block = True).
    End of line. in_block is True, so DON'T flush current_line yet.

  Line 1, block comment state:
    'c','o','m','m','e','n','t',' ' → skipped.
    '*'  → peek ahead: '*/' → exit block comment. i += 2.
    ' '  → output ' '. current_line = ['a', ' ', ' ']
    'b'  → output 'b'. current_line = ['a', ' ', ' ', 'b']
    End of line. in_block is False. Flush: "a  b".

  Result: ["a  b"]

  The block comment merged two source lines into one output line.
  Content before the /* and after the */ joined together.
```

## Approaches

### Approach 1: State Machine

<details>
<summary>📝 Explanation</summary>

Maintain a boolean `in_block` for whether we're inside a block comment, and a `current_line` buffer for the output line being built.

For each source line, walk character by character:
- **Normal state + `//`:** Break out of the line (line comment, ignore rest).
- **Normal state + `/*`:** Set `in_block = True`, skip two characters.
- **Normal state + other:** Append to `current_line`.
- **Block state + `*/`:** Set `in_block = False`, skip two characters.
- **Block state + other:** Skip (inside comment).

At the end of each source line: if we're not in a block comment and `current_line` has content, flush it to the result. If we ARE in a block comment, don't flush (the current_line continues to the next source line, which is how block comments merge lines).

**Time:** O(n) where n is total characters across all lines. Each character is examined once.
**Space:** O(n) for the output.

The state machine approach is clean and handles all edge cases. The key insight is that `current_line` persists across source lines during block comments, which naturally handles line merging.

</details>

## Edge Cases

| Input | Why It Matters |
|---|---|
| Block comment spanning 3+ lines | Middle lines are entirely removed |
| `/*` and `*/` on same line | Block comment within a single line |
| Line comment after block comment end | `*/ // rest` - block ends, then line comment starts |
| Entire line is a comment | Output line would be empty, skip it |
| No comments at all | Return input unchanged |

## Common Pitfalls

- **Forgetting to handle line merging:** When a block comment spans lines, the text before `/*` on line N and after `*/` on line M become one output line.
- **Processing `//` inside block comments:** In block state, `//` is just content to skip, not a line comment start.
- **Empty lines after comment removal:** Lines that become empty after removing comments should be excluded from the output.

## Interview Tips

> "This is a state machine problem with two states: normal and in-block-comment. I'll process character by character with one character of lookahead for the two-character sequences. The tricky part is that block comments can merge lines."

## DE Application

Preprocessing config files and SQL scripts before execution. Removing comments from generated SQL, stripping annotation lines from data files, cleaning up vendor-provided scripts. The state machine approach generalizes to any context-dependent parsing (inside strings vs outside strings, inside tags vs outside tags).

## Related Problems

- [385. Mini Parser](https://leetcode.com/problems/mini-parser/) - Nested structure parsing
- [736. Parse Lisp Expression](https://leetcode.com/problems/parse-lisp-expression/) - Complex expression parsing
````

---

## Problem 4: Validate IP Address (LeetCode #468)

### `problems/p468_validate_ip_address.py`

```python
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
```

### `problems/p468_validate_ip_address_test.py`

```python
"""Tests for LeetCode 468: Validate IP Address."""

import pytest

from .p468_validate_ip_address import valid_ip_address


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
```

### `problems/468_validate_ip_address.md`

````markdown
# Validate IP Address (LeetCode #468)

## Problem Statement

Given a string `queryIP`, return "IPv4" if it's a valid IPv4 address, "IPv6" if valid IPv6, or "Neither."

IPv4: four decimal numbers (0-255) separated by dots. No leading zeros (except "0" itself).
IPv6: eight groups of 1-4 hexadecimal digits separated by colons.

## Thought Process

1. **Determine the type first:** If it contains dots, try IPv4 validation. If colons, try IPv6. If neither (or both), return "Neither."
2. **Split and validate each part:** For IPv4, split on "." and check each of the 4 segments. For IPv6, split on ":" and check each of the 8 groups.
3. **Rule-based validation:** Each segment has specific rules (numeric range, length, allowed characters, no leading zeros). Check them systematically.

## Worked Example

Split the string on the appropriate delimiter, then validate each segment against the format rules. The approach is methodical: check the number of segments first, then validate each one individually. No clever algorithms needed - just careful rule application.

```
Input: "172.16.254.01"

  Contains '.' → try IPv4.
  Split on '.': ["172", "16", "254", "01"]
  4 parts? Yes.

  Validate each part:
    "172": all digits? Yes. Leading zero? No. int("172")=172 <= 255? Yes. ✓
    "16":  all digits? Yes. Leading zero? No. int("16")=16 <= 255? Yes. ✓
    "254": all digits? Yes. Leading zero? No. int("254")=254 <= 255? Yes. ✓
    "01":  all digits? Yes. Leading zero? len("01")>1 and starts with '0'. INVALID.

  Result: "Neither"

Input: "2001:db8:85a3:0:0:8A2E:370:7334"

  Contains ':' → try IPv6.
  Split on ':': ["2001", "db8", "85a3", "0", "0", "8A2E", "370", "7334"]
  8 groups? Yes.

  Validate each group:
    "2001": length 1-4? Yes. All hex? Yes. ✓
    "db8":  length 1-4? Yes. All hex? Yes. ✓
    "85a3": length 1-4? Yes. All hex? Yes. ✓
    "0":    length 1-4? Yes. All hex? Yes. ✓
    "0":    ✓
    "8A2E": length 1-4? Yes. All hex (mixed case OK)? Yes. ✓
    "370":  ✓
    "7334": ✓

  Result: "IPv6"
```

## Approaches

### Approach 1: Split and Validate

<details>
<summary>📝 Explanation</summary>

Determine the address type by checking for "." or ":". Split the string on the appropriate delimiter and validate each segment.

For IPv4, each segment must:
1. Be non-empty
2. Contain only digits (no letters, no signs)
3. Have no leading zeros (unless the segment is exactly "0")
4. Represent a number between 0 and 255

For IPv6, each group must:
1. Be non-empty
2. Be 1-4 characters long
3. Contain only hexadecimal characters (0-9, a-f, A-F)

The validation is straightforward but the edge cases are numerous. Leading zeros in IPv4, mixed case in IPv6, empty segments from consecutive delimiters ("1..3"), trailing delimiters ("1.2.3.4.") - each needs explicit handling.

**Time:** O(n) where n is the string length. Split is O(n), validation of each part is O(part length).
**Space:** O(n) for the split result.

This isn't algorithmically interesting but it tests your ability to handle edge cases systematically. Interviewers watch for whether you enumerate the validation rules upfront or discover them one by one through bugs.

</details>

## Edge Cases

| Input | Expected | Why |
|---|---|---|
| `"0.0.0.0"` | IPv4 | All zeros is valid |
| `"01.01.01.01"` | Neither | Leading zeros in IPv4 |
| `"255.255.255.255"` | IPv4 | Max values |
| `"256.0.0.0"` | Neither | Out of range |
| `"1.2.3"` | Neither | Too few segments |
| `"1.2.3.4.5"` | Neither | Too many segments |
| `"1..2.3"` | Neither | Empty segment |
| `""` | Neither | Empty string |

## Common Pitfalls

- **`int()` accepting leading zeros:** Python's `int("01")` returns 1 without error. You must explicitly check for leading zeros by inspecting the string.
- **Negative numbers:** `"-1"` passes `isdigit()` → False in Python (correctly), but check for the minus sign explicitly if using other approaches.
- **Trailing delimiters:** `"1.2.3.4."` splits into 5 parts (last one empty). The length check catches this.
- **IPv6 case sensitivity:** Both "a" and "A" are valid hex digits.

## Interview Tips

> "I'll determine the type by checking for dots vs colons, split on the delimiter, then validate each segment against the format rules. The key is being systematic about edge cases - leading zeros, range checks, empty segments."

**This problem tests attention to detail, not algorithmic thinking.** State your validation rules upfront before coding. It shows structured thinking.

## DE Application

Input validation in data pipelines. IP addresses in log files, network data, access logs - they need validation before loading into analytics tables. The same pattern applies to validating email formats, phone numbers, URLs and any structured string data. Validate early in the pipeline and quarantine invalid records.

## Related Problems

- [93. Restore IP Addresses](https://leetcode.com/problems/restore-ip-addresses/) - Generate valid IPs from digit string
- [751. IP to CIDR](https://leetcode.com/problems/ip-to-cidr/) - IP range operations
````

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== Tests ==="
uv run pytest patterns/09_string_parsing/problems/ -v --tb=short 2>&1 | tail -20

echo ""
echo "=== Worked Examples start with prose ==="
for f in patterns/09_string_parsing/problems/722_remove_comments.md patterns/09_string_parsing/problems/468_validate_ip_address.md; do
    first=$(awk '/^## Worked Example/{found=1; next} found && /\S/{print; exit}' "$f")
    echo "$(basename $f): $first" | head -c 80
    echo ""
done
```
