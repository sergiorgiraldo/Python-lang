# Remove Comments (LeetCode #722)

🔗 [LeetCode 722: Remove Comments](https://leetcode.com/problems/remove-comments/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

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

**What the interviewer evaluates:** State machine design (tracking in_block_comment state) tests systematic thinking. Handling the interaction between line comments and block comments (a `//` inside a `/* */` is not a line comment) tests attention to edge cases. Clean state transition logic with clear variable names is more important than clever tricks.

## DE Application

Preprocessing config files and SQL scripts before execution. Removing comments from generated SQL, stripping annotation lines from data files, cleaning up vendor-provided scripts. The state machine approach generalizes to any context-dependent parsing (inside strings vs outside strings, inside tags vs outside tags).

## At Scale

The state machine approach (tracking whether you're inside a block comment) is O(n) and processes line by line: O(1) memory per line. For a 100K-line source file, this is instant. At scale, the relevant application is processing structured text files in pipelines: stripping headers, removing metadata lines, extracting content from markup. These are streaming operations that don't need the full file in memory. In production, comment removal and text cleanup are pre-processing steps before indexing or analysis. The state machine pattern (tracking "am I inside X?") generalizes to any delimited-region processing: SQL string literals, HTML tags, XML CDATA sections.

## Related Problems

- [385. Mini Parser](https://leetcode.com/problems/mini-parser/) - Nested structure parsing
- [736. Parse Lisp Expression](https://leetcode.com/problems/parse-lisp-expression/) - Complex expression parsing
