# CC Prompt: Create Pattern 08 Stack (Part 3 of 5)

## What This Prompt Does

Creates problems 3-4: Evaluate RPN (LeetCode 150) and Daily Temperatures (LeetCode 739).

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Every .md Worked Example starts with a prose paragraph
- Every approach explanation teaches the "why" not just the "what"

---

## Problem 3: Evaluate Reverse Polish Notation (LeetCode #150)

### `problems/p150_eval_rpn.py`

```python
"""
LeetCode 150: Evaluate Reverse Polish Notation

Pattern: Stack - Expression evaluation
Difficulty: Medium
Time Complexity: O(n)
Space Complexity: O(n)
"""

import operator


def eval_rpn(tokens: list[str]) -> int:
    """
    Evaluate a Reverse Polish Notation expression.

    RPN (postfix) places operators after their operands:
    "2 3 +" means 2 + 3. The stack handles operator precedence
    naturally - no parentheses needed.

    Rules:
    - Numbers push onto the stack.
    - Operators pop two operands, compute, push the result.
    - The second-popped value is the LEFT operand (order matters for - and /).
    - Division truncates toward zero (int(a / b), not a // b).
    """
    ops = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": lambda a, b: int(a / b),  # truncate toward zero
    }

    stack: list[int] = []

    for token in tokens:
        if token in ops:
            b = stack.pop()  # right operand (most recent)
            a = stack.pop()  # left operand
            stack.append(ops[token](a, b))
        else:
            stack.append(int(token))

    return stack[0]
```

### `problems/p150_eval_rpn_test.py`

```python
"""Tests for LeetCode 150: Evaluate Reverse Polish Notation."""

import pytest

from .p150_eval_rpn import eval_rpn


class TestEvalRPN:
    """Core expression evaluation."""

    def test_simple_addition(self) -> None:
        assert eval_rpn(["2", "1", "+"]) == 3

    def test_complex_expression(self) -> None:
        assert eval_rpn(["2", "1", "+", "3", "*"]) == 9

    def test_division_truncation(self) -> None:
        assert eval_rpn(["10", "3", "/"]) == 3

    def test_negative_division(self) -> None:
        # -1 / 2 should truncate toward zero = 0 (not -1)
        tokens = ["4", "13", "5", "/", "+"]
        assert eval_rpn(tokens) == 6

    def test_longer_expression(self) -> None:
        tokens = ["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]
        assert eval_rpn(tokens) == 22

    def test_single_number(self) -> None:
        assert eval_rpn(["42"]) == 42

    def test_subtraction_order(self) -> None:
        # "5 3 -" means 5 - 3 = 2, not 3 - 5
        assert eval_rpn(["5", "3", "-"]) == 2

    def test_negative_numbers(self) -> None:
        assert eval_rpn(["-2", "3", "+"]) == 1

    def test_all_operators(self) -> None:
        assert eval_rpn(["6", "2", "+", "3", "*", "2", "/"]) == 12

    def test_negative_result(self) -> None:
        assert eval_rpn(["3", "5", "-"]) == -2
```

### `problems/150_eval_rpn.md`

````markdown
# Evaluate Reverse Polish Notation (LeetCode #150)

## Problem Statement

Evaluate the value of an arithmetic expression in Reverse Polish Notation (RPN). Valid operators are +, -, * and /. Each operand may be an integer or another expression. Division truncates toward zero.

Example: `["2", "1", "+", "3", "*"]` evaluates to `((2 + 1) * 3) = 9`

## Thought Process

1. **What is RPN?** Also called postfix notation. Operators come after their operands: "2 3 +" means "add 2 and 3." The advantage: no parentheses needed and no operator precedence rules. The evaluation order is unambiguous.
2. **Why a stack?** Numbers accumulate until an operator consumes them. The most recent numbers are the operands for the next operator. That's LIFO.
3. **Operand order matters:** For subtraction and division, the first popped value is the RIGHT operand, the second is the LEFT. "5 3 -" means 5 - 3, not 3 - 5.

## Worked Example

Push numbers onto the stack. When an operator appears, pop two numbers, apply the operator and push the result back. The stack naturally handles nested expressions because inner expressions resolve first (they were pushed more recently).

```
Input: ["4", "13", "5", "/", "+"]

  "4"  → number. Push.    Stack: [4]
  "13" → number. Push.    Stack: [4, 13]
  "5"  → number. Push.    Stack: [4, 13, 5]
  "/"  → operator. Pop b=5, pop a=13. Compute 13/5 = 2 (truncate). Push 2.
                           Stack: [4, 2]
  "+"  → operator. Pop b=2, pop a=4. Compute 4+2 = 6. Push 6.
                           Stack: [6]

  Return stack[0] = 6.

This is equivalent to: 4 + (13 / 5) = 4 + 2 = 6.
The parentheses are implicit in the evaluation order.

More complex: ["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]

  Push 10, 6, 9, 3.       Stack: [10, 6, 9, 3]
  "+": pop 3, 9 → 12.     Stack: [10, 6, 12]
  Push -11.                Stack: [10, 6, 12, -11]
  "*": pop -11, 12 → -132. Stack: [10, 6, -132]
  "/": pop -132, 6 → int(6/-132) = 0. Stack: [10, 0]
  "*": pop 0, 10 → 0.     Stack: [0]
  Push 17.                 Stack: [0, 17]
  "+": pop 17, 0 → 17.    Stack: [17]
  Push 5.                  Stack: [17, 5]
  "+": pop 5, 17 → 22.    Stack: [22]

  Return 22.
```

## Approaches

### Approach 1: Stack with Operator Map

<details>
<summary>📝 Explanation</summary>

Build a dict mapping operator strings to functions (using Python's `operator` module or lambdas). Walk through the tokens. If a token is an operator, pop two values, apply the function, push the result. Otherwise parse the token as an integer and push it.

Division is the tricky part: Python's `//` (floor division) rounds toward negative infinity, but the problem wants truncation toward zero. `int(a / b)` handles this correctly: `int(-7 / 2)` gives `-3` (truncated toward zero), while `-7 // 2` gives `-4` (floored).

After processing all tokens, exactly one value remains on the stack. That's the answer.

**Time:** O(n) - one pass through the tokens. Each token causes at most one push and one pop.
**Space:** O(n) - the stack holds at most (n+1)/2 values (when all tokens are numbers followed by all operators).

</details>

<details>
<summary>💡 Hint</summary>

Numbers go on the stack. Operators consume the top two items and push the result back.

</details>

## Edge Cases

| Input | Expected | Why |
|---|---|---|
| `["42"]` | 42 | Single number, no operators |
| `["5", "3", "-"]` | 2 | Operand order: 5-3, not 3-5 |
| `["-2", "3", "+"]` | 1 | Negative number as input |
| `["10", "3", "/"]` | 3 | Division truncates toward zero |

## Common Pitfalls

- **Operand order for - and /:** The first pop is the RIGHT operand, second pop is LEFT. Swapping them gives wrong results for non-commutative operators.
- **Division truncation:** Using `//` instead of `int(a/b)` breaks for negative results. `-7 // 2 = -4` but the expected answer is `-3`.
- **Treating negative numbers as operators:** "-2" is a number, not a subtraction. Check `token in ops` not `token[0] in ops`.

## Interview Tips

> "RPN evaluates unambiguously without parentheses. I'll use a stack: push numbers, pop two on operators, push the result. The key detail is operand order for subtraction and division."

## DE Application

Config-driven pipelines sometimes use expression evaluation for computed columns: `"revenue", "cost", "-", "tax", "*"`. Stack-based evaluation handles these without building a full expression parser. Also useful for evaluating filter expressions in query builders.

## Related Problems

- [224. Basic Calculator](https://leetcode.com/problems/basic-calculator/) - Infix with parentheses (harder)
- [227. Basic Calculator II](https://leetcode.com/problems/basic-calculator-ii/) - Infix with precedence
````

---

## Problem 4: Daily Temperatures (LeetCode #739)

### `problems/p739_daily_temperatures.py`

```python
"""
LeetCode 739: Daily Temperatures

Pattern: Stack - Monotonic decreasing stack
Difficulty: Medium
Time Complexity: O(n)
Space Complexity: O(n)
"""


def daily_temperatures(temperatures: list[int]) -> list[int]:
    """
    For each day, find how many days until a warmer temperature.

    Maintain a stack of indices with decreasing temperatures.
    When a new temperature is warmer than the stack top, it's
    the answer for that stacked day. Pop and record the distance.

    Days remaining in the stack at the end never see a warmer day (answer = 0).
    """
    n = len(temperatures)
    result = [0] * n
    stack: list[int] = []  # indices of unresolved days

    for i in range(n):
        while stack and temperatures[i] > temperatures[stack[-1]]:
            prev = stack.pop()
            result[prev] = i - prev
        stack.append(i)

    return result


def daily_temperatures_brute(temperatures: list[int]) -> list[int]:
    """Brute force: for each day, scan forward for a warmer day. O(n^2)."""
    n = len(temperatures)
    result = [0] * n

    for i in range(n):
        for j in range(i + 1, n):
            if temperatures[j] > temperatures[i]:
                result[i] = j - i
                break

    return result
```

### `problems/p739_daily_temperatures_test.py`

```python
"""Tests for LeetCode 739: Daily Temperatures."""

import pytest

from .p739_daily_temperatures import daily_temperatures, daily_temperatures_brute


@pytest.mark.parametrize("func", [daily_temperatures, daily_temperatures_brute])
class TestDailyTemperatures:
    """Test both implementations."""

    def test_example(self, func) -> None:
        assert func([73, 74, 75, 71, 69, 72, 76, 73]) == [1, 1, 4, 2, 1, 1, 0, 0]

    def test_decreasing(self, func) -> None:
        assert func([76, 75, 74, 73]) == [0, 0, 0, 0]

    def test_increasing(self, func) -> None:
        assert func([70, 71, 72, 73]) == [1, 1, 1, 0]

    def test_single(self, func) -> None:
        assert func([50]) == [0]

    def test_two_elements_warmer(self, func) -> None:
        assert func([30, 60]) == [1, 0]

    def test_two_elements_same(self, func) -> None:
        assert func([50, 50]) == [0, 0]

    def test_plateau_then_spike(self, func) -> None:
        assert func([70, 70, 70, 80]) == [3, 2, 1, 0]

    def test_all_same(self, func) -> None:
        assert func([65, 65, 65, 65]) == [0, 0, 0, 0]

    def test_valley_pattern(self, func) -> None:
        assert func([80, 70, 60, 70, 80]) == [0, 2, 1, 1, 0]
```

### `problems/739_daily_temperatures.md`

````markdown
# Daily Temperatures (LeetCode #739)

## Problem Statement

Given an array of daily temperatures, return an array where each element tells you how many days you have to wait until a warmer temperature. If no future day is warmer, the answer is 0.

Example: `[73, 74, 75, 71, 69, 72, 76, 73]` → `[1, 1, 4, 2, 1, 1, 0, 0]`

## Thought Process

1. **Brute force:** For each day, scan forward until you find a warmer day. O(n²). Works but slow for large inputs.
2. **The key insight:** When we encounter a warm day, it resolves ALL recent cooler days at once. Day 76 in the example resolves both day 75 (waited 4 days) and day 72 (waited 1 day). We need a structure that gives us "all recent unresolved days" - that's a stack.
3. **Monotonic stack:** The stack holds indices of days still waiting for a warmer day. Their temperatures are in decreasing order (a day that's warmer than the one below it would have already resolved it). When a new temperature beats the top, pop and record.

## Worked Example

The stack holds indices of days whose "next warmer day" hasn't been found yet. The temperatures at those indices are always decreasing from bottom to top. When a new day is warmer than the top, it resolves that day and potentially several below it.

```
Input: [73, 74, 75, 71, 69, 72, 76, 73]
Result initialized to all zeros: [0, 0, 0, 0, 0, 0, 0, 0]

i=0 (73): Stack empty. Push 0.           Stack: [0(73)]
i=1 (74): 74 > 73. Pop 0. result[0]=1-0=1. Push 1.
                                          Stack: [1(74)]
i=2 (75): 75 > 74. Pop 1. result[1]=2-1=1. Push 2.
                                          Stack: [2(75)]
i=3 (71): 71 < 75. Push 3.               Stack: [2(75), 3(71)]
i=4 (69): 69 < 71. Push 4.               Stack: [2(75), 3(71), 4(69)]
i=5 (72): 72 > 69. Pop 4. result[4]=5-4=1.
          72 > 71. Pop 3. result[3]=5-3=2.
          72 < 75. Stop. Push 5.          Stack: [2(75), 5(72)]
i=6 (76): 76 > 72. Pop 5. result[5]=6-5=1.
          76 > 75. Pop 2. result[2]=6-2=4.
          Stack empty. Push 6.            Stack: [6(76)]
i=7 (73): 73 < 76. Push 7.               Stack: [6(76), 7(73)]

Remaining (indices 6, 7) stay 0 - no warmer day follows.
Result: [1, 1, 4, 2, 1, 1, 0, 0]

Total operations: 8 pushes + 6 pops = 14. Each index pushed once,
popped at most once. O(n).
```

## Approaches

### Approach 1: Brute Force

<details>
<summary>📝 Explanation</summary>

For each day i, scan forward from i+1 until you find a temperature higher than temperatures[i]. Record the distance. If you reach the end without finding one, the answer is 0.

**Time:** O(n²) - for each of n days, potentially scan up to n-1 future days.
**Space:** O(1) extra (besides the output array).

Simple and correct. State it first, then optimize.

</details>

### Approach 2: Monotonic Decreasing Stack

<details>
<summary>📝 Explanation</summary>

Maintain a stack of indices. The temperatures at these indices are in decreasing order from bottom to top (hence "monotonic decreasing"). This invariant is maintained by popping everything that the current temperature exceeds.

For each day i:
1. While the stack is non-empty and `temperatures[i] > temperatures[stack[-1]]`: pop the top index. The answer for that popped day is `i - popped_index`.
2. Push i onto the stack.

After processing all days, any indices remaining in the stack never found a warmer day (their answer stays 0 from initialization).

Why O(n): each index is pushed exactly once and popped at most once. The inner while loop across all iterations of the outer for loop executes at most n times total. So the total work is at most 2n operations.

**Time:** O(n) - each element pushed and popped at most once.
**Space:** O(n) - stack can hold up to n indices (all decreasing temperatures).

This is the standard monotonic stack pattern. The same structure solves "next greater element," "stock span" and "largest rectangle."

</details>

## Edge Cases

| Input | Expected | Why |
|---|---|---|
| `[50]` | `[0]` | Single day, nothing to compare |
| `[30, 60]` | `[1, 0]` | Two days, second is warmer |
| `[80, 70, 60]` | `[0, 0, 0]` | Decreasing - no warmer day exists |
| `[60, 60, 60]` | `[0, 0, 0]` | Same temp is NOT warmer (strictly greater) |
| `[60, 60, 80]` | `[2, 1, 0]` | Equal temps skip, 80 resolves both |

## Common Pitfalls

- **Using >= instead of > for the comparison:** Same temperature is NOT warmer. Must be strictly greater.
- **Storing temperatures instead of indices:** You need the index to compute the distance. Store indices, look up temperatures.
- **Forgetting that remaining stack items get 0:** They're already 0 from initialization. No extra cleanup needed.

## Interview Tips

> "This is a 'next greater element' problem. I'll use a monotonic decreasing stack of indices. When a warmer day arrives, it resolves all recent cooler days at once. Each element is pushed and popped at most once, so it's O(n) despite the nested loop."

**Key talking point:** Explaining the O(n) complexity of a nested loop is a strong signal. "The inner while loop doesn't restart from scratch each iteration. Across all outer iterations, the total pops equal the total pushes, which is n."

## DE Application

Time-series analysis: "for each data point, when does the metric next exceed this value?" Monitoring dashboards that show "time until next spike" for each measurement. The monotonic stack answers this in a single pass instead of scanning forward from each point.

## Related Problems

- [496. Next Greater Element I](https://leetcode.com/problems/next-greater-element-i/) - Simpler version
- [503. Next Greater Element II](https://leetcode.com/problems/next-greater-element-ii/) - Circular array
- [84. Largest Rectangle in Histogram](https://leetcode.com/problems/largest-rectangle-in-histogram/) - Monotonic increasing stack
````

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== Tests ==="
uv run pytest patterns/08_stack/problems/p150* patterns/08_stack/problems/p739* -v --tb=short 2>&1 | tail -15

echo ""
echo "=== Worked Examples start with prose ==="
for f in patterns/08_stack/problems/150_eval_rpn.md patterns/08_stack/problems/739_daily_temperatures.md; do
    first=$(awk '/^## Worked Example/{found=1; next} found && /\S/{print; exit}' "$f")
    echo "$(basename $f): $first" | head -c 80
    echo ""
done
```
