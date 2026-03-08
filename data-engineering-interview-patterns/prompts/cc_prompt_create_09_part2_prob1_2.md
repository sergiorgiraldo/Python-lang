# CC Prompt: Create Pattern 09 String Parsing (Part 2 of 5)

## What This Prompt Does

Creates problems 1-2: Encode and Decode Strings (LeetCode 271) and Decode String (LeetCode 394).

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Every .md Worked Example starts with a prose paragraph
- Every approach explanation teaches the "why" not just the "what"

---

## Problem 1: Encode and Decode Strings (LeetCode #271)

### `problems/p271_encode_decode_strings.py`

```python
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
```

### `problems/p271_encode_decode_strings_test.py`

```python
"""Tests for LeetCode 271: Encode and Decode Strings."""

import pytest

from .p271_encode_decode_strings import (
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
        strs = ["café", "naïve", "日本語"]
        assert dec(enc(strs)) == strs

    def test_newlines(self, enc, dec) -> None:
        strs = ["line1\nline2", "line3"]
        assert dec(enc(strs)) == strs
```

### `problems/271_encode_decode_strings.md`

````markdown
# Encode and Decode Strings (LeetCode #271)

## Problem Statement

Design an algorithm to encode a list of strings into a single string and decode it back. The encoded string is transmitted over a network, so the decode function must reconstruct the original list exactly.

The strings can contain any characters, including the delimiter you choose.

## Thought Process

1. **The challenge:** You can't just join with a delimiter (like comma) because the strings themselves might contain that delimiter. "a,b" and "c" encoded as "a,b,c" is ambiguous - is it ["a,b", "c"] or ["a", "b", "c"]?
2. **Length prefixing:** If you tell the decoder how many characters to read, the content doesn't matter. "5#hello" means "read 5 characters after the #." Even if a string contains "#" or digits, the length tells you exactly where it ends.
3. **Alternative: escaping.** Escape special characters in the content. Works but more error-prone and slower for large inputs.

## Worked Example

Length prefixing makes the encoding unambiguous regardless of string content. The decoder reads the number before the delimiter, then reads exactly that many characters. No scanning for delimiters within the content, no ambiguity.

```
Encode: ["hello", "wor#ld", "", "42"]

  "hello"  → len=5 → "5#hello"
  "wor#ld" → len=6 → "6#wor#ld"
  ""       → len=0 → "0#"
  "42"     → len=2 → "2#42"

  Encoded: "5#hello6#wor#ld0#2#42"

Decode: "5#hello6#wor#ld0#2#42"

  i=0: read digits until '#'. digits="5". j=1 (the '#').
       length=5. read s[2:7] = "hello". i=7.
  i=7: read digits until '#'. digits="6". j=8.
       length=6. read s[9:15] = "wor#ld". i=15.
       (the '#' inside "wor#ld" doesn't confuse us because
       we're reading exactly 6 characters, not scanning for '#')
  i=15: digits="0". j=16. length=0. read s[17:17] = "". i=17.
  i=17: digits="2". j=18. length=2. read s[19:21] = "42". i=21.

  Result: ["hello", "wor#ld", "", "42"]
```

## Approaches

### Approach 1: Length Prefix Encoding

<details>
<summary>📝 Explanation</summary>

Encode: for each string, prepend its length followed by a delimiter character (e.g., "#"). Concatenate all encoded strings.

Decode: read digits until you hit "#" to get the length. Read exactly that many characters. Repeat until the end of the encoded string.

This is the same principle as HTTP's Content-Length header, protocol buffers' length-delimited encoding, and Kafka's message framing. The length prefix makes the boundary unambiguous regardless of content.

**Time:** O(n) where n is total characters across all strings. Each character is read once during encode and once during decode.
**Space:** O(n) for the encoded string. The overhead is the length prefix per string, which is typically a few bytes.

This is the standard approach. It's simple, fast and handles all edge cases (empty strings, delimiter in content, any character).

</details>

### Approach 2: Escape-Based Encoding

<details>
<summary>📝 Explanation</summary>

Choose a delimiter (comma) and an escape character (slash). Encode: replace any slash in the content with "//" and any comma with "/,". Join with comma. Decode: walk character by character, treating "/" as an escape prefix.

The advantage: the encoded format is human-readable. "hello,world" encodes as "hello,world" (no overhead for clean strings).

The disadvantage: every character must be inspected for escaping during both encode and decode. Escape sequences compound ("/" becomes "//" in encoding, so a string full of slashes doubles in size). Edge cases around consecutive escape characters are easy to get wrong.

**Time:** O(n) but with higher constant factor (every character checked for escaping).
**Space:** O(n), potentially up to 2n if content is full of escape characters.

Mention this as an alternative but note length-prefix is more robust. In DE work, you'll see both: CSV uses escaping (quote doubling), while binary protocols use length prefixing.

</details>

## Edge Cases

| Input | Why It Matters |
|---|---|
| `[""]` | Empty string is valid. Length prefix handles: "0#" |
| `[]` | Empty list. Encoded as empty string "" |
| `["a#b", "c#d"]` | Delimiter in content. Length prefix handles it |
| `["123", "45"]` | Numbers that look like length prefixes. Not ambiguous because we always read digits then "#" |
| `["hello\nworld"]` | Newline in content. Length prefix doesn't care |

## Common Pitfalls

- **Using `str.find("#")` in decode:** This finds the first "#" in the remaining string, but if the content contains "#", it'll split in the wrong place. Read digits character by character until you hit "#".
- **Off-by-one in slice indices:** After reading the length at position j, the content starts at j+1 and has `length` characters. `s[j+1 : j+1+length]`.
- **Forgetting empty strings:** `"0#"` is a valid encoding of one empty string.

## Interview Tips

> "The key insight is that content-based delimiters are ambiguous. Length prefixing removes ambiguity by telling the decoder exactly how many characters to read. It's the same principle as HTTP Content-Length."

**Follow-ups:**
- "What if you need to handle streaming decode?" → Read length, then read that many bytes from the stream. Works naturally.
- "What about compression?" → Compress the entire encoded string. Don't compress individual strings (overhead per string).

## DE Application

Data serialization for transport. When you send a batch of records through a message queue or write them to a file, you need a framing protocol. Length-prefix encoding is the simplest reliable approach. Avro, Protobuf and Parquet all use variants of length-prefix framing internally.

## Related Problems

- [443. String Compression](https://leetcode.com/problems/string-compression/) - Related encoding
- [394. Decode String](https://leetcode.com/problems/decode-string/) - Nested encoding
````

---

## Problem 2: Decode String (LeetCode #394)

### `problems/p394_decode_string.py`

```python
"""
LeetCode 394: Decode String

Pattern: String Parsing - Stack-based nested expansion
Difficulty: Medium
Time Complexity: O(n * max_expansion) where n is input length
Space Complexity: O(n) for the stack
"""


def decode_string(s: str) -> str:
    """
    Decode an encoded string like "3[a2[c]]" → "accaccacc".

    Rules:
    - k[encoded_string] means repeat encoded_string k times.
    - Nesting is allowed: the encoded_string can itself contain k[...].

    Stack approach: push the current string and repeat count when we
    see '['. Pop and build the result when we see ']'. The stack
    handles arbitrary nesting depth.
    """
    stack: list[tuple[str, int]] = []
    current = ""
    k = 0

    for char in s:
        if char.isdigit():
            k = k * 10 + int(char)  # handle multi-digit numbers
        elif char == "[":
            stack.append((current, k))
            current = ""
            k = 0
        elif char == "]":
            prev_string, repeat_count = stack.pop()
            current = prev_string + current * repeat_count
        else:
            current += char

    return current


def decode_string_recursive(s: str) -> str:
    """
    Recursive approach. Each '[' starts a recursive call,
    each ']' returns from it.
    """

    def helper(index: int) -> tuple[str, int]:
        result = ""
        k = 0

        while index < len(s):
            char = s[index]
            if char.isdigit():
                k = k * 10 + int(char)
                index += 1
            elif char == "[":
                decoded, index = helper(index + 1)
                result += decoded * k
                k = 0
            elif char == "]":
                return result, index + 1
            else:
                result += char
                index += 1

        return result, index

    result, _ = helper(0)
    return result
```

### `problems/p394_decode_string_test.py`

```python
"""Tests for LeetCode 394: Decode String."""

import pytest

from .p394_decode_string import decode_string, decode_string_recursive


@pytest.mark.parametrize("func", [decode_string, decode_string_recursive])
class TestDecodeString:
    """Test both implementations."""

    def test_simple(self, func) -> None:
        assert func("3[a]") == "aaa"

    def test_nested(self, func) -> None:
        assert func("3[a2[c]]") == "accaccacc"

    def test_adjacent(self, func) -> None:
        assert func("2[abc]3[cd]ef") == "abcabccdcdcdef"

    def test_deeply_nested(self, func) -> None:
        assert func("2[a2[b3[c]]]") == "abcccbcccabcccbccc"

    def test_no_encoding(self, func) -> None:
        assert func("abc") == "abc"

    def test_single_repeat(self, func) -> None:
        assert func("1[abc]") == "abc"

    def test_multi_digit(self, func) -> None:
        assert func("10[a]") == "aaaaaaaaaa"

    def test_empty_brackets(self, func) -> None:
        assert func("3[]") == ""

    def test_letters_between(self, func) -> None:
        assert func("ab3[c]de") == "abcccde"

    def test_complex(self, func) -> None:
        assert func("3[a]2[bc]") == "aaabcbc"
```

### `problems/394_decode_string.md`

````markdown
# Decode String (LeetCode #394)

## Problem Statement

Given an encoded string, return its decoded version. The encoding rule is: `k[encoded_string]` means the `encoded_string` is repeated `k` times. Nesting is allowed.

Examples:
- `"3[a]"` → `"aaa"`
- `"3[a2[c]]"` → `"accaccacc"`
- `"2[abc]3[cd]ef"` → `"abcabccdcdcdef"`

## Thought Process

1. **Why a stack?** The encoding can nest: `3[a2[c]]` means "expand the inner part first." The inner expansion must complete before the outer one can use its result. That's LIFO - same as Pattern 08.
2. **What goes on the stack?** When we see `[`, we push two things: the string built so far (before this bracket), and the repeat count. We start fresh inside the brackets.
3. **What happens at `]`?** Pop the saved state. The current string is what was inside the brackets. Multiply it by the repeat count and append it to the saved prefix.

## Worked Example

The stack saves context at each nesting level. When we enter a bracket, we save "what we had before" and "how many times to repeat what's inside." When we close the bracket, we combine the saved prefix with the repeated inner content.

```
Input: "3[a2[c]]"

  '3' → digit. k = 3.
  '[' → push (current="", k=3). Reset: current="", k=0.
        Stack: [("", 3)]
  'a' → letter. current = "a".
  '2' → digit. k = 2.
  '[' → push (current="a", k=2). Reset: current="", k=0.
        Stack: [("", 3), ("a", 2)]
  'c' → letter. current = "c".
  ']' → pop ("a", 2). current = "a" + "c"*2 = "a" + "cc" = "acc".
        Stack: [("", 3)]
  ']' → pop ("", 3). current = "" + "acc"*3 = "accaccacc".
        Stack: []

  Result: "accaccacc"

Step-by-step nesting:
  Inner: 2[c] → "cc"
  Combined: a + "cc" → "acc"
  Outer: 3["acc"] → "accaccacc"
```

## Approaches

### Approach 1: Stack

<details>
<summary>📝 Explanation</summary>

Walk through the string character by character, maintaining a current string and current repeat count:

- **Digit:** Build up the repeat count (handle multi-digit: `k = k * 10 + int(char)`).
- **`[`:** Push `(current_string, repeat_count)` onto the stack. Reset both.
- **`]`:** Pop `(prev_string, count)` from the stack. Set `current = prev_string + current * count`.
- **Letter:** Append to current string.

After processing all characters, `current` holds the fully decoded result.

The stack depth equals the maximum nesting level. Each character is processed once, but string concatenation inside the loop can be expensive for large repeat counts (10[10[10[a]]] expands to 1000 characters from 14 input characters).

**Time:** O(n * max_expansion) where n is the decoded output length. Each character in the output is produced once.
**Space:** O(n) for the stack and intermediate strings.

</details>

### Approach 2: Recursive

<details>
<summary>📝 Explanation</summary>

Each `[` triggers a recursive call that processes everything until the matching `]`. The recursion naturally handles nesting: inner brackets are resolved by deeper recursive calls before the outer call uses the result.

The recursive function returns both the decoded string and the index where it stopped (after the `]`). This lets the caller know where to continue processing.

Functionally equivalent to the stack approach. The call stack replaces the explicit stack. Some interviewers prefer seeing the stack version because it's more explicit about what's being saved and restored.

**Time:** O(n * max_expansion) - same as stack.
**Space:** O(depth) for recursion stack where depth is the maximum nesting level.

</details>

## Edge Cases

| Input | Expected | Why |
|---|---|---|
| `"abc"` | `"abc"` | No encoding, just letters |
| `"10[a]"` | `"aaaaaaaaaa"` | Multi-digit repeat count |
| `"3[]"` | `""` | Empty brackets, repeated 0 characters = empty |
| `"1[abc]"` | `"abc"` | Repeat count of 1, no change |

## Common Pitfalls

- **Single-digit assumption:** `k = int(char)` breaks for "10[a]". Must accumulate: `k = k * 10 + int(char)`.
- **String concatenation performance:** Building strings with `+=` in Python creates a new string each time. For very large outputs, use a list and join. For interview purposes, `+=` is fine.
- **Forgetting to reset k:** After pushing to the stack, reset k to 0. Otherwise the next digit compounds with the previous count.

## Interview Tips

> "This is a nested structure problem. I'll use a stack to save context when entering brackets and restore it when leaving. The stack stores the string built so far and the repeat count."

**Connection to Pattern 08:** This is the same pattern as Valid Parentheses but with computation at each nesting level. The bracket matching tracks nesting depth, and the stack carries data through each level.

## DE Application

Template and config expansion in pipelines. Systems like dbt use Jinja templates with nested macros: `{{ macro_a(macro_b(value)) }}`. The expansion is stack-based - resolve inner macros first, then outer ones. Same principle as this problem.

## Related Problems

- [726. Number of Atoms](https://leetcode.com/problems/number-of-atoms/) - Similar nested counting
- [1190. Reverse Substrings Between Each Pair of Parentheses](https://leetcode.com/problems/reverse-substrings-between-each-pair-of-parentheses/) - Stack with transformation
````

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== Tests ==="
uv run pytest patterns/09_string_parsing/problems/ -v --tb=short 2>&1 | tail -15

echo ""
echo "=== Worked Examples start with prose ==="
for f in patterns/09_string_parsing/problems/271_encode_decode_strings.md patterns/09_string_parsing/problems/394_decode_string.md; do
    first=$(awk '/^## Worked Example/{found=1; next} found && /\S/{print; exit}' "$f")
    echo "$(basename $f): $first" | head -c 80
    echo ""
done
```
