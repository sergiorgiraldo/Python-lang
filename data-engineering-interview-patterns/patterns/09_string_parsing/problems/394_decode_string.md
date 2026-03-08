# Decode String (LeetCode #394)

🔗 [LeetCode 394: Decode String](https://leetcode.com/problems/decode-string/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

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

**What the interviewer evaluates:** Stack-based nested processing tests implementation precision. Handling the multiplier (which can be multi-digit) and the nesting (stack push on `[`, pop and multiply on `]`) correctly is the challenge. Off-by-one errors in character processing are common. Mentioning output size limits and template expansion safety shows production awareness.

## DE Application

Template and config expansion in pipelines. Systems like dbt use Jinja templates with nested macros: `{{ macro_a(macro_b(value)) }}`. The expansion is stack-based - resolve inner macros first, then outer ones. Same principle as this problem.

## At Scale

The stack holds nested multiplier/string pairs. Memory is O(nesting depth * average string length). For shallow nesting (2-3 levels) with short patterns, this is negligible. The risk: deeply nested patterns with high multipliers produce exponentially large output. `3[3[3[3[a]]]]` expands to 81 characters. `100[100[100[a]]]` expands to 1M characters. In production, template expansion (Jinja in dbt, variable substitution in configs) has the same risk. Always set expansion limits to prevent accidental memory bombs. The stack-based decoder is O(output size) - the output itself can be the bottleneck, not the algorithm.

## Related Problems

- [726. Number of Atoms](https://leetcode.com/problems/number-of-atoms/) - Similar nested counting
- [1190. Reverse Substrings Between Each Pair of Parentheses](https://leetcode.com/problems/reverse-substrings-between-each-pair-of-parentheses/) - Stack with transformation
