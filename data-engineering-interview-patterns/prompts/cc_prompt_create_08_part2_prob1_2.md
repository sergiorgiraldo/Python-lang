# CC Prompt: Create Pattern 08 Stack (Part 2 of 5)

## What This Prompt Does

Creates problems 1-2: Valid Parentheses (LeetCode 20) and Min Stack (LeetCode 155). Each problem gets a .py file, _test.py file and .md file with deep teaching.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Every .md Worked Example starts with a prose paragraph
- Every approach explanation teaches the "why" not just the "what"

---

## Problem 1: Valid Parentheses (LeetCode #20)

### `problems/p020_valid_parentheses.py`

```python
"""
LeetCode 20: Valid Parentheses

Pattern: Stack - Matching/Validation
Difficulty: Easy
Time Complexity: O(n)
Space Complexity: O(n)
"""


def is_valid(s: str) -> bool:
    """
    Check if brackets are properly matched and nested.

    Push opening brackets onto a stack. When a closing bracket
    appears, check that the top of the stack is the matching
    opener. If not, or if the stack is empty, the string is invalid.
    At the end, the stack must be empty (all openers were closed).
    """
    stack: list[str] = []
    pairs = {")": "(", "}": "{", "]": "["}

    for char in s:
        if char in pairs.values():
            stack.append(char)
        elif char in pairs:
            if not stack or stack[-1] != pairs[char]:
                return False
            stack.pop()

    return len(stack) == 0
```

### `problems/p020_valid_parentheses_test.py`

```python
"""Tests for LeetCode 20: Valid Parentheses."""

import pytest

from .p020_valid_parentheses import is_valid


class TestValidParentheses:
    """Core bracket matching."""

    def test_simple_parens(self) -> None:
        assert is_valid("()") is True

    def test_multiple_types(self) -> None:
        assert is_valid("()[]{}") is True

    def test_nested(self) -> None:
        assert is_valid("({[]})") is True

    def test_mismatch(self) -> None:
        assert is_valid("(]") is False

    def test_wrong_order(self) -> None:
        assert is_valid("([)]") is False

    def test_unclosed(self) -> None:
        assert is_valid("((") is False

    def test_extra_closer(self) -> None:
        assert is_valid("))") is False

    def test_empty_string(self) -> None:
        assert is_valid("") is True

    def test_single_opener(self) -> None:
        assert is_valid("(") is False

    def test_single_closer(self) -> None:
        assert is_valid(")") is False

    def test_deeply_nested(self) -> None:
        assert is_valid("(((())))") is True

    def test_alternating(self) -> None:
        assert is_valid("(){}[](){}[]") is True
```

### `problems/020_valid_parentheses.md`

````markdown
# Valid Parentheses (LeetCode #20)

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

## DE Application

Validating nested structures in data pipelines: JSON files with unclosed braces, XML with mismatched tags, SQL with unbalanced parentheses. A stack-based validator catches these errors with a single pass and gives the exact position of the first mismatch.

## Related Problems

- [22. Generate Parentheses](https://leetcode.com/problems/generate-parentheses/) - Generate all valid combinations
- [32. Longest Valid Parentheses](https://leetcode.com/problems/longest-valid-parentheses/) - DP/stack hybrid
- [1249. Minimum Remove to Make Valid](https://leetcode.com/problems/minimum-remove-to-make-valid-parentheses/) - Fix invalid strings
````

---

## Problem 2: Min Stack (LeetCode #155)

### `problems/p155_min_stack.py`

```python
"""
LeetCode 155: Min Stack

Pattern: Stack - Augmented data structure
Difficulty: Medium
Time Complexity: O(1) for all operations
Space Complexity: O(n)
"""


class MinStackTuple:
    """
    Stack that supports push, pop, top and getMin in O(1).

    Each entry stores (value, current_minimum). The minimum at any
    point is the min of the new value and the previous minimum.
    This way, popping an element also "restores" the previous minimum.
    """

    def __init__(self) -> None:
        self.stack: list[tuple[int, int]] = []

    def push(self, val: int) -> None:
        current_min = min(val, self.stack[-1][1]) if self.stack else val
        self.stack.append((val, current_min))

    def pop(self) -> None:
        self.stack.pop()

    def top(self) -> int:
        return self.stack[-1][0]

    def get_min(self) -> int:
        return self.stack[-1][1]


class MinStackTwoStacks:
    """
    Alternative: separate main stack and min-tracking stack.

    The min stack only pushes when a new minimum (or equal) arrives.
    Pops from min stack only when the popped value equals the current min.
    Uses less space when minimums change infrequently.
    """

    def __init__(self) -> None:
        self.stack: list[int] = []
        self.min_stack: list[int] = []

    def push(self, val: int) -> None:
        self.stack.append(val)
        if not self.min_stack or val <= self.min_stack[-1]:
            self.min_stack.append(val)

    def pop(self) -> None:
        val = self.stack.pop()
        if val == self.min_stack[-1]:
            self.min_stack.pop()

    def top(self) -> int:
        return self.stack[-1]

    def get_min(self) -> int:
        return self.min_stack[-1]
```

### `problems/p155_min_stack_test.py`

```python
"""Tests for LeetCode 155: Min Stack."""

import pytest

from .p155_min_stack import MinStackTuple, MinStackTwoStacks


@pytest.mark.parametrize("StackClass", [MinStackTuple, MinStackTwoStacks])
class TestMinStack:
    """Test both implementations."""

    def test_basic_operations(self, StackClass) -> None:
        s = StackClass()
        s.push(-2)
        s.push(0)
        s.push(-3)
        assert s.get_min() == -3
        s.pop()
        assert s.top() == 0
        assert s.get_min() == -2

    def test_single_element(self, StackClass) -> None:
        s = StackClass()
        s.push(42)
        assert s.top() == 42
        assert s.get_min() == 42

    def test_increasing_order(self, StackClass) -> None:
        s = StackClass()
        for val in [1, 2, 3, 4, 5]:
            s.push(val)
        assert s.get_min() == 1
        s.pop()
        assert s.get_min() == 1

    def test_decreasing_order(self, StackClass) -> None:
        s = StackClass()
        for val in [5, 4, 3, 2, 1]:
            s.push(val)
        assert s.get_min() == 1
        s.pop()
        assert s.get_min() == 2
        s.pop()
        assert s.get_min() == 3

    def test_duplicate_minimums(self, StackClass) -> None:
        s = StackClass()
        s.push(0)
        s.push(1)
        s.push(0)
        assert s.get_min() == 0
        s.pop()
        assert s.get_min() == 0

    def test_negative_values(self, StackClass) -> None:
        s = StackClass()
        s.push(-1)
        s.push(-2)
        s.push(-3)
        assert s.get_min() == -3
        s.pop()
        assert s.get_min() == -2

    def test_pop_and_push_again(self, StackClass) -> None:
        s = StackClass()
        s.push(3)
        s.push(1)
        s.pop()
        s.push(2)
        assert s.get_min() == 2  # min was 1 but we popped it
        # Actually min should be min(3, 2) = 2
        s.pop()
        assert s.get_min() == 3
```

### `problems/155_min_stack.md`

````markdown
# Min Stack (LeetCode #155)

## Problem Statement

Design a stack that supports push, pop, top and retrieving the minimum element, all in O(1) time.

## Thought Process

1. **The challenge:** A regular stack gives O(1) push/pop/top but finding the minimum requires scanning the entire stack (O(n)). We need to track the minimum as elements come and go.
2. **Key insight:** When we push a value, the minimum either changes (if the new value is smaller) or stays the same. When we pop, the minimum reverts to whatever it was before that push. This "snapshot" behavior is exactly what a stack captures.
3. **Two approaches:** Store the current minimum alongside each value (tuple approach), or maintain a separate stack that tracks only the minimums (two-stack approach).

## Worked Example

The core idea: every position in the stack has a "what's the minimum from here down?" answer. We record that answer at push time so we never have to recompute it. When we pop, the answer for the previous position is already recorded.

```
Tuple approach - each entry stores (value, min_so_far):

  push(-2): min = -2.          stack: [(-2, -2)]
  push(0):  min = min(0,-2)=-2. stack: [(-2,-2), (0,-2)]
  push(-3): min = min(-3,-2)=-3. stack: [(-2,-2), (0,-2), (-3,-3)]
  getMin(): stack[-1][1] = -3. ✓
  pop():    remove (-3,-3).     stack: [(-2,-2), (0,-2)]
  top():    stack[-1][0] = 0. ✓
  getMin(): stack[-1][1] = -2. ✓  (minimum "restored" automatically)

Two-stack approach - main stack + min stack:

  push(-2): stack=[-2], min_stack=[-2] (-2 <= nothing, push to min)
  push(0):  stack=[-2,0], min_stack=[-2] (0 > -2, don't push)
  push(-3): stack=[-2,0,-3], min_stack=[-2,-3] (-3 <= -2, push)
  getMin(): min_stack[-1] = -3. ✓
  pop():    pop -3 from stack. -3 == min_stack[-1] → pop min too.
            stack=[-2,0], min_stack=[-2]
  top():    stack[-1] = 0. ✓
  getMin(): min_stack[-1] = -2. ✓

Both approaches: all operations O(1). The tuple approach uses more
memory (every entry stores a min). The two-stack approach only stores
mins when they change, saving space when many consecutive values
are above the current minimum.
```

## Approaches

### Approach 1: Tuple Stack (Value + Min Pairs)

<details>
<summary>📝 Explanation</summary>

Store each entry as a tuple `(value, current_minimum)`. When pushing, the new minimum is `min(val, previous_minimum)`. When getting the minimum, just read the second element of the top tuple.

The insight: every stack position has a fixed "minimum from here down" that never changes once recorded. When we pop, the previous entry's minimum is automatically correct because it was calculated when *that* entry was pushed (before the now-popped entry existed).

**Time:** O(1) for all operations.
**Space:** O(n) - each entry stores two values.

Simpler to implement and reason about. The overhead is storing an extra integer per entry.

</details>

### Approach 2: Two Separate Stacks

<details>
<summary>📝 Explanation</summary>

Maintain a main stack for values and a separate min_stack that only tracks minimums. Push to min_stack when the new value is ≤ the current minimum. Pop from min_stack when the popped value equals the current minimum.

The `<=` (not `<`) is critical: if the same minimum value is pushed twice, the min_stack must record it twice. Otherwise popping one copy would incorrectly remove the minimum even though another copy remains.

**Time:** O(1) for all operations.
**Space:** O(n) worst case, but often less than the tuple approach if the minimum changes infrequently (e.g., pushing [1, 5, 8, 3, 7, 9] only adds 1 and 3 to min_stack).

</details>

## Edge Cases

| Scenario | Why It Matters |
|---|---|
| Duplicate minimums | `push(0), push(0), pop()` - min must still be 0 |
| All same values | Min never changes, but two-stack must still track correctly |
| Decreasing sequence | Every push changes the minimum |
| Single element | getMin after one push must work |

## Common Pitfalls

- **Two-stack: using `<` instead of `<=`:** Must push to min_stack when value equals the current min, not just when strictly less.
- **Forgetting empty checks:** getMin/top on an empty stack should be handled (problem guarantees valid calls, but good to note).

## Interview Tips

> "I need O(1) min retrieval, which means I can't scan the stack each time. I'll snapshot the minimum at each push by storing (value, current_min) tuples. Popping automatically restores the previous minimum."

**Follow-ups:**
- "Can you optimize space?" → Two-stack approach stores fewer mins.
- "What about a max stack?" → Same pattern, track max instead of min.
- "What if you also need O(1) median?" → Two heaps (pattern 05), not stacks.

## DE Application

Tracking running minimums or maximums in streaming data without rescanning. For example: "what's the lowest latency we've seen since the pipeline started?" Push each observation, and getMin tells you instantly. If you need to handle a sliding window, combine with a deque.

## Related Problems

- [716. Max Stack](https://leetcode.com/problems/max-stack/) - Same idea with max
- [239. Sliding Window Maximum](https://leetcode.com/problems/sliding-window-maximum/) - Deque-based running max
````

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== Files created ==="
ls patterns/08_stack/problems/p020* patterns/08_stack/problems/020* patterns/08_stack/problems/p155* patterns/08_stack/problems/155* 2>/dev/null

echo ""
echo "=== Tests ==="
uv run pytest patterns/08_stack/ -v --tb=short 2>&1 | tail -15

echo ""
echo "=== Worked Examples start with prose ==="
for f in patterns/08_stack/problems/020_valid_parentheses.md patterns/08_stack/problems/155_min_stack.md; do
    first=$(awk '/^## Worked Example/{found=1; next} found && /\S/{print; exit}' "$f")
    echo "$(basename $f): $first" | head -c 80
    echo ""
done
```
