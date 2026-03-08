# Validate IP Address (LeetCode #468)

🔗 [LeetCode 468: Validate IP Address](https://leetcode.com/problems/validate-ip-address/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

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

**What the interviewer evaluates:** This tests systematic thinking under edge case pressure. Enumerating all validation rules before writing code (rather than discovering them through failed test cases) is the key signal. The problem is straightforward algorithmically but easy to get wrong in details. Mentioning that production code uses library functions (`ipaddress` module, Spark built-ins) rather than hand-rolled validation shows engineering pragmatism.

## DE Application

Input validation in data pipelines. IP addresses in log files, network data, access logs - they need validation before loading into analytics tables. The same pattern applies to validating email formats, phone numbers, URLs and any structured string data. Validate early in the pipeline and quarantine invalid records.

## At Scale

Validation is O(n) per string with O(1) memory. For 1B log records, the bottleneck is I/O (reading the data) not the validation logic. In production pipelines, IP validation is done with regex or built-in library functions (Python's `ipaddress` module, Spark's built-in IP parsing). Custom validation code like this is rarely written at scale. The important pattern is the validation strategy: validate early in the pipeline, reject or quarantine invalid records and track error rates. If 0.1% of 1B records have malformed IPs, that's 1M bad records. Silently dropping them loses data. Quarantining them for investigation preserves data quality. In SQL, `SAFE.NET.IP_FROM_STRING` (BigQuery) returns NULL for invalid IPs, which you can then filter or flag.

## Related Problems

- [93. Restore IP Addresses](https://leetcode.com/problems/restore-ip-addresses/) - Generate valid IPs from digit string
- [751. IP to CIDR](https://leetcode.com/problems/ip-to-cidr/) - IP range operations
