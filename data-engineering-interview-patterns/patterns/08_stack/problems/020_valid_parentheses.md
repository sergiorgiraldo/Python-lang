# Valid Parentheses (LeetCode #20)

🔗 [LeetCode 20: Valid Parentheses](https://leetcode.com/problems/valid-parentheses/)

> **Difficulty:** Easy | **Interview Frequency:** Very Common

## Problem Statement

Given a string `s` containing just the characters `(`, `)`, `{`, `}`, `[` and `]`, determine if the input string is valid.

A string is valid if:
- Open brackets are closed by the same type of brackets
- Open brackets are closed in the correct order
- Every close bracket has a corresponding open bracket of the same type

## Thought Process

1. **Why a stack?** Brackets nest. The most recent opener is the one that must be closed first. That's LIFO - exactly what a stack does.
2. **The matching rule:** When we see a closer, the top of the stack must be its matching opener. If it's not (or the stack is empty), the string is invalid.
3. **End state:** After processing all characters, the stack must be empty. A non-empty stack means unclosed openers remain.

## Worked Example

The stack tracks "what am I currently inside?" Each opener pushes context, each closer pops and verifies. If we see `]` but the top of the stack is `(`, we have a nesting error - we're trying to close a bracket that isn't the most recent one opened.

```
Input: "({[]})"

  '(' → opener. Push.     Stack: ['(']
  '{' → opener. Push.     Stack: ['(', '{']
  '[' → opener. Push.     Stack: ['(', '{', '[']
  ']' → closer. Top='['. Matches ']'? Yes. Pop.  Stack: ['(', '{']
  '}' → closer. Top='{'. Matches '}'? Yes. Pop.  Stack: ['(']
  ')' → closer. Top='('. Matches ')'? Yes. Pop.  Stack: []

  Stack empty at end → valid. Every opener had a matching closer in the right order.

Input: "([)]"

  '(' → push.    Stack: ['(']
  '[' → push.    Stack: ['(', '[']
  ')' → closer. Top='['. Matches ')'? No. → INVALID.

  The brackets overlap instead of nesting. '(' opened before '[',
  but ')' tries to close before ']'. Stack catches this immediately.

Input: "(("

  '(' → push.    Stack: ['(']
  '(' → push.    Stack: ['(', '(']

  End of string. Stack not empty (2 unclosed openers) → INVALID.
```

## Approaches

### Approach 1: Stack with Dict Matching

<details>
<summary>📝 Explanation</summary>

Build a dict mapping each closer to its opener: `{')': '(', '}': '{', ']': '['}`. Scan the string character by character.

For each character:
- If it's an opener (one of the dict values), push it onto the stack.
- If it's a closer (one of the dict keys), check two things: is the stack non-empty, and does the top match this closer's opener? If either check fails, return False. If both pass, pop the top.

After processing all characters, the stack should be empty. If it's not, there are unclosed openers.

**Time:** O(n) - one pass through the string. Each character causes at most one push and one pop.
**Space:** O(n) - in the worst case (all openers like "(((("), the stack holds every character.

This is the standard solution. The dict makes the matching logic clean and extensible (easy to add new bracket types).

</details>

<details>
<summary>💡 Hint</summary>

What data structure lets you check "what was the most recent opener?" in O(1)?

</details>

<details>
<summary>💻 Code</summary>

See `p020_valid_parentheses.py`

</details>

## Edge Cases

| Input | Expected | Why |
|---|---|---|
| `""` | True | Empty string has no unmatched brackets |
| `"("` | False | Single opener, never closed |
| `")"` | False | Closer with no opener |
| `"((()))"` | True | Deeply nested, all matched |
| `"([)]"` | False | Overlapping, not nesting |

## Common Pitfalls

- **Forgetting to check stack empty before popping:** A closer when the stack is empty should return False, not crash.
- **Checking `len(stack) == 0` only at the end:** Must also check during processing (for extra closers).
- **Using a string instead of a list:** String concatenation is O(n) per operation in Python. Use a list.

## Interview Tips

> "This is a classic stack problem. Brackets nest, so the most recent opener is always the one that must close first. I'll use a dict to map closers to openers and a stack to track what's currently open."

**Follow-ups interviewers ask:**
- "What if the string contains non-bracket characters?" → Skip them (only process brackets).
- "What about HTML tags like `<div>` and `</div>`?" → Same pattern but parse tag names instead of single characters.
- "Can you do it without a stack?" → A counter works for single bracket types, but not for multiple types (you lose ordering information).

**What the interviewer evaluates:** This is the canonical "do you know stacks?" problem. Clean, fast execution is expected. The dict mapping closers to openers is the standard approach. Mentioning streaming validation for large files shows production awareness. This is usually a warm-up.

## DE Application

Validating nested structures in data pipelines: JSON files with unclosed braces, XML with mismatched tags, SQL with unbalanced parentheses. A stack-based validator catches these errors with a single pass and gives the exact position of the first mismatch.

## At Scale

The stack holds at most O(n) characters in the worst case (all openers). For a 1GB JSON file, worst case stack depth is the maximum nesting depth, typically a few hundred levels - not 1B characters. Memory is bounded by nesting depth, not input size. This makes bracket validation streaming-friendly: read characters one at a time, push/pop the stack and never hold the full input. Production JSON validators (Python's json module, streaming parsers like ijson) use exactly this approach. For validating files before ingestion in a pipeline, a streaming validator catches malformed data without loading the entire file.

## Related Problems

- [22. Generate Parentheses](https://leetcode.com/problems/generate-parentheses/) - Generate all valid combinations
- [32. Longest Valid Parentheses](https://leetcode.com/problems/longest-valid-parentheses/) - DP/stack hybrid
- [1249. Minimum Remove to Make Valid](https://leetcode.com/problems/minimum-remove-to-make-valid-parentheses/) - Fix invalid strings
