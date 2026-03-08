# Encode and Decode Strings (LeetCode #271)

🔗 [LeetCode 271: Encode and Decode Strings](https://leetcode.com/problems/encode-and-decode-strings/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

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

**What the interviewer evaluates:** Designing a serialization scheme that handles arbitrary strings (including the delimiter character) tests protocol design thinking. The length-prefix approach is the standard solution. Mentioning that this is how real protocols work (TCP framing, Protobuf) shows systems knowledge. The follow-up "what about streaming?" (answer: the length prefix tells you exactly how many bytes to read next) connects to network programming.

## DE Application

Data serialization for transport. When you send a batch of records through a message queue or write them to a file, you need a framing protocol. Length-prefix encoding is the simplest reliable approach. Avro, Protobuf and Parquet all use variants of length-prefix framing internally.

## At Scale

Length-prefix encoding (write length, then delimiter, then string) produces output of size O(total characters + n * delimiter overhead). For 10M strings averaging 50 characters, the encoded form is ~510MB (500MB for strings + ~10MB for length prefixes). This is the same encoding that network protocols use (TCP length-prefixed frames, Protobuf varint-prefixed fields). At scale, serialization format choice matters enormously: JSON is human-readable but 2-5x larger than binary formats. Protobuf, Avro, Parquet and MessagePack are production choices that use length-prefixed or schema-based encoding for efficiency. Understanding the algorithmic basis (length-prefixed encoding) helps you reason about why binary formats are faster and smaller.

## Related Problems

- [443. String Compression](https://leetcode.com/problems/string-compression/) - Related encoding
- [394. Decode String](https://leetcode.com/problems/decode-string/) - Nested encoding
