# CC Prompt: Create Pattern 08 Stack (Part 5 of 5)

## What This Prompt Does

Creates 3 DE scenarios + benchmark module for pattern 08.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Every .md Worked Example starts with a prose paragraph
- DE scenarios include both .py (runnable) and .md (documented)

---

## DE Scenario 1: Nested Structure Validation

### `de_scenarios/nested_validation.py`

```python
"""
DE Scenario: Validate nested structures (JSON-like bracket matching).

Real-world application: validating JSON files, XML documents, SQL
parentheses, or config files before processing in a pipeline.

Run: uv run python -m patterns.08_stack.de_scenarios.nested_validation
"""

from collections import Counter


def validate_brackets(text: str) -> tuple[bool, str]:
    """
    Validate matching brackets in a text string.

    Returns (is_valid, error_message). Checks (), [], {}.
    Skips non-bracket characters.
    """
    stack: list[tuple[str, int]] = []  # (bracket, position)
    pairs = {")": "(", "]": "[", "}": "{"}

    for i, char in enumerate(text):
        if char in pairs.values():
            stack.append((char, i))
        elif char in pairs:
            if not stack:
                return False, f"Unexpected '{char}' at position {i}"
            top_char, top_pos = stack[-1]
            if top_char != pairs[char]:
                return False, (
                    f"Mismatched '{char}' at position {i}, "
                    f"expected closing for '{top_char}' from position {top_pos}"
                )
            stack.pop()

    if stack:
        char, pos = stack[-1]
        return False, f"Unclosed '{char}' from position {pos}"

    return True, "Valid"


def validate_json_structure(json_str: str) -> tuple[bool, str]:
    """
    Lightweight JSON structure validation (brackets and braces only).

    Does not parse values or validate JSON syntax fully.
    Catches the structural errors that break json.loads().
    """
    # Track bracket types and whether we're inside a string
    stack: list[tuple[str, int]] = []
    in_string = False
    escape_next = False

    for i, char in enumerate(json_str):
        if escape_next:
            escape_next = False
            continue
        if char == "\\":
            escape_next = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue

        if char in "{[":
            stack.append((char, i))
        elif char in "}]":
            expected = "{" if char == "}" else "["
            if not stack:
                return False, f"Unexpected '{char}' at position {i}"
            if stack[-1][0] != expected:
                return False, (
                    f"Expected closing for '{stack[-1][0]}' from position "
                    f"{stack[-1][1]}, got '{char}' at position {i}"
                )
            stack.pop()

    if stack:
        return False, f"Unclosed '{stack[-1][0]}' from position {stack[-1][1]}"

    return True, "Valid"


if __name__ == "__main__":
    print("=== Bracket Validation ===")

    tests = [
        ('{"users": [{"name": "alice"}, {"name": "bob"}]}', True),
        ('{"users": [{"name": "alice"}, {"name": "bob"}]', False),
        ('SELECT * FROM (SELECT id FROM (users)', False),
        ("((()))", True),
        ("({[]})", True),
        ("([)]", False),
    ]

    for text, expected in tests:
        valid, msg = validate_brackets(text)
        status = "PASS" if valid == expected else "FAIL"
        print(f"  [{status}] {text[:40]}... → {msg}")

    print("\n=== JSON Structure Validation ===")

    json_tests = [
        ('{"key": "value with \\"escaped\\" quotes"}', True),
        ('{"key": [1, 2, {"nested": true}]}', True),
        ('{"key": [1, 2, {"nested": true}]', False),
    ]

    for text, expected in json_tests:
        valid, msg = validate_json_structure(text)
        status = "PASS" if valid == expected else "FAIL"
        print(f"  [{status}] {text[:50]}... → {msg}")
```

### `de_scenarios/nested_validation.md`

````markdown
# DE Scenario: Nested Structure Validation

## Real-World Context

Every data pipeline that ingests JSON, XML or config files needs to validate structure. A missing closing brace in a 500MB JSON file will either crash `json.loads()` with an unhelpful error or silently corrupt downstream data. Stack-based validation catches these errors in a single pass and reports the exact position.

## Worked Example

Bracket validation is Valid Parentheses (problem 20) applied to real data. The addition: track positions so error messages are actionable ("unclosed '{' at position 42" instead of just "invalid").

```
Input: '{"users": [{"name": "alice"}, {"name": "bob"}]'

  i=0  '{' → push ('{', 0).      Stack: [('{',0)]
  i=10 '[' → push ('[', 10).     Stack: [('{',0), ('[',10)]
  i=11 '{' → push ('{', 11).     Stack: [('{',0), ('[',10), ('{',11)]
  i=27 '}' → matches '{' at 11. Pop.  Stack: [('{',0), ('[',10)]
  i=30 '{' → push ('{', 30).     Stack: [('{',0), ('[',10), ('{',30)]
  i=44 '}' → matches '{' at 30. Pop.  Stack: [('{',0), ('[',10)]
  i=45 ']' → matches '[' at 10. Pop.  Stack: [('{',0)]
  End of string. Stack not empty.

  Error: "Unclosed '{' from position 0"
  Fix: add closing '}' at the end.
```
````

---

## DE Scenario 2: Expression Evaluation

### `de_scenarios/expression_eval.py`

```python
"""
DE Scenario: Evaluate config-driven pipeline expressions.

Real-world application: computed columns, filter expressions,
and conditional logic in config-driven data pipelines.

Run: uv run python -m patterns.08_stack.de_scenarios.expression_eval
"""


def evaluate_config_expression(
    expression: str, variables: dict[str, float]
) -> float:
    """
    Evaluate a simple config expression with variables.

    Supports: +, -, *, / operators, parentheses, and variable substitution.
    Uses the shunting-yard algorithm (infix to postfix) then evaluates.
    """
    tokens = _tokenize(expression, variables)
    postfix = _to_postfix(tokens)
    return _eval_postfix(postfix)


def _tokenize(
    expression: str, variables: dict[str, float]
) -> list[str | float]:
    """Tokenize an expression, substituting variables."""
    tokens: list[str | float] = []
    i = 0
    while i < len(expression):
        if expression[i].isspace():
            i += 1
        elif expression[i] in "+-*/()":
            tokens.append(expression[i])
            i += 1
        elif expression[i].isdigit() or expression[i] == ".":
            j = i
            while j < len(expression) and (expression[j].isdigit() or expression[j] == "."):
                j += 1
            tokens.append(float(expression[i:j]))
            i = j
        elif expression[i].isalpha() or expression[i] == "_":
            j = i
            while j < len(expression) and (expression[j].isalnum() or expression[j] == "_"):
                j += 1
            var_name = expression[i:j]
            if var_name not in variables:
                raise ValueError(f"Unknown variable: {var_name}")
            tokens.append(variables[var_name])
            i = j
        else:
            raise ValueError(f"Unexpected character: {expression[i]}")
    return tokens


def _to_postfix(tokens: list[str | float]) -> list[str | float]:
    """Convert infix tokens to postfix using shunting-yard algorithm."""
    output: list[str | float] = []
    op_stack: list[str] = []
    precedence = {"+": 1, "-": 1, "*": 2, "/": 2}

    for token in tokens:
        if isinstance(token, float):
            output.append(token)
        elif token == "(":
            op_stack.append(token)
        elif token == ")":
            while op_stack and op_stack[-1] != "(":
                output.append(op_stack.pop())
            if op_stack:
                op_stack.pop()  # remove the "("
        elif token in precedence:
            while (
                op_stack
                and op_stack[-1] != "("
                and op_stack[-1] in precedence
                and precedence[op_stack[-1]] >= precedence[token]
            ):
                output.append(op_stack.pop())
            op_stack.append(token)

    while op_stack:
        output.append(op_stack.pop())

    return output


def _eval_postfix(tokens: list[str | float]) -> float:
    """Evaluate a postfix expression."""
    stack: list[float] = []
    ops = {
        "+": lambda a, b: a + b,
        "-": lambda a, b: a - b,
        "*": lambda a, b: a * b,
        "/": lambda a, b: a / b,
    }

    for token in tokens:
        if isinstance(token, float):
            stack.append(token)
        else:
            b = stack.pop()
            a = stack.pop()
            stack.append(ops[token](a, b))

    return stack[0]


if __name__ == "__main__":
    print("=== Config Expression Evaluation ===")

    variables = {
        "revenue": 1000000,
        "cost": 750000,
        "tax_rate": 0.21,
        "discount": 50000,
    }

    expressions = [
        ("revenue - cost", 250000),
        ("(revenue - cost) * tax_rate", 52500),
        ("revenue - cost - discount", 200000),
        ("(revenue - cost - discount) * (1 + tax_rate)", 242000),
    ]

    for expr, expected in expressions:
        result = evaluate_config_expression(expr, variables)
        status = "PASS" if abs(result - expected) < 0.01 else "FAIL"
        print(f"  [{status}] {expr} = {result} (expected {expected})")
```

### `de_scenarios/expression_eval.md`

````markdown
# DE Scenario: Expression Evaluation for Config-Driven Pipelines

## Real-World Context

Config-driven pipelines define computed columns as expressions: `"profit": "revenue - cost"`. Evaluating these at runtime requires expression parsing. The shunting-yard algorithm converts infix expressions to postfix using a stack, then evaluates the postfix using a second stack. Same mechanics as Eval RPN (problem 150) with a preprocessing step.

## Worked Example

Two stacks in sequence. First, the shunting-yard algorithm converts infix (human-readable) to postfix (machine-evaluable) using an operator stack. Then the evaluation stack computes the result, exactly like problem 150.

```
Expression: "(revenue - cost) * tax_rate"
Variables: revenue=1000000, cost=750000, tax_rate=0.21

Step 1: Tokenize with variable substitution
  (1000000 - 750000) * 0.21

Step 2: Shunting-yard (infix → postfix)
  '('      → push to op_stack. Op: ['(']
  1000000  → output. Out: [1000000]
  '-'      → push. Op: ['(', '-']
  750000   → output. Out: [1000000, 750000]
  ')'      → pop until '('. Pop '-'. Out: [1000000, 750000, '-']. Op: []
  '*'      → push. Op: ['*']
  0.21     → output. Out: [1000000, 750000, '-', 0.21]
  End      → flush op_stack. Out: [1000000, 750000, '-', 0.21, '*']

Step 3: Evaluate postfix (same as Eval RPN)
  1000000  → push. Stack: [1000000]
  750000   → push. Stack: [1000000, 750000]
  '-'      → pop 750000, 1000000. Compute 1000000-750000=250000. Push.
             Stack: [250000]
  0.21     → push. Stack: [250000, 0.21]
  '*'      → pop 0.21, 250000. Compute 250000*0.21=52500. Push.
             Stack: [52500]

  Result: 52500
```
````

---

## DE Scenario 3: Monotonic Time Series

### `de_scenarios/monotonic_time_series.py`

```python
"""
DE Scenario: Monotonic stack for time-series analysis.

Real-world application: finding the next threshold breach for each
data point in a monitoring stream. Same pattern as Daily Temperatures.

Run: uv run python -m patterns.08_stack.de_scenarios.monotonic_time_series
"""

from dataclasses import dataclass


@dataclass
class TimeSeriesPoint:
    """A single time-series data point."""

    timestamp: str
    value: float


def next_threshold_breach(
    data: list[TimeSeriesPoint], threshold: float
) -> dict[str, str | None]:
    """
    For each data point, find the next point that exceeds the threshold.

    Returns a dict mapping each timestamp to the timestamp of the
    next breach, or None if no future breach exists.

    Uses a monotonic stack: points waiting for a breach are on the stack.
    When a breach arrives, it resolves all waiting points.
    """
    result: dict[str, str | None] = {}
    stack: list[int] = []  # indices of unresolved points

    for i, point in enumerate(data):
        while stack and point.value > threshold:
            idx = stack.pop()
            result[data[idx].timestamp] = point.timestamp
        if point.value <= threshold:
            stack.append(i)
        else:
            result[point.timestamp] = None  # already above threshold

    # Remaining unresolved points
    while stack:
        idx = stack.pop()
        result[data[idx].timestamp] = None

    return result


def next_greater_value(data: list[TimeSeriesPoint]) -> dict[str, tuple[str, float] | None]:
    """
    For each data point, find the next point with a strictly greater value.

    Classic "next greater element" applied to time series. Same as
    Daily Temperatures but with timestamps instead of indices.
    """
    result: dict[str, tuple[str, float] | None] = {}
    stack: list[int] = []

    for i, point in enumerate(data):
        while stack and point.value > data[stack[-1]].value:
            idx = stack.pop()
            result[data[idx].timestamp] = (point.timestamp, point.value)
        stack.append(i)

    while stack:
        idx = stack.pop()
        result[data[idx].timestamp] = None

    return result


if __name__ == "__main__":
    print("=== Next Threshold Breach ===")

    data = [
        TimeSeriesPoint("08:00", 45),
        TimeSeriesPoint("08:05", 52),
        TimeSeriesPoint("08:10", 48),
        TimeSeriesPoint("08:15", 41),
        TimeSeriesPoint("08:20", 55),
        TimeSeriesPoint("08:25", 38),
        TimeSeriesPoint("08:30", 60),
    ]

    breaches = next_threshold_breach(data, threshold=50)
    for ts, breach_ts in sorted(breaches.items()):
        print(f"  {ts}: next breach at {breach_ts}")

    print("\n=== Next Greater Value ===")

    greater = next_greater_value(data)
    for ts, result in sorted(greater.items()):
        if result:
            print(f"  {ts} ({data[[p.timestamp for p in data].index(ts)].value})"
                  f" → {result[0]} ({result[1]})")
        else:
            print(f"  {ts}: no greater value found")
```

### `de_scenarios/monotonic_time_series.md`

````markdown
# DE Scenario: Monotonic Stack for Time-Series Analysis

## Real-World Context

Monitoring systems track metrics over time. A common question: "for each data point, when does the metric next exceed a threshold (or the current value)?" Scanning forward from each point is O(n²). A monotonic stack answers this in O(n) by resolving multiple waiting points when a spike arrives.

## Worked Example

Same pattern as Daily Temperatures (problem 739). Points below the threshold sit on the stack, waiting. When a point above the threshold arrives, it resolves all waiting points at once.

```
Threshold: 50
Data: [(08:00, 45), (08:05, 52), (08:10, 48), (08:15, 41),
       (08:20, 55), (08:25, 38), (08:30, 60)]

  08:00 (45): below threshold. Push.    Stack: [08:00(45)]
  08:05 (52): above threshold. Resolves 08:00.
              result[08:00] = 08:05. Pop.
              08:05 itself is above → result[08:05] = None.  Stack: []
  08:10 (48): below. Push.              Stack: [08:10(48)]
  08:15 (41): below. Push.              Stack: [08:10(48), 08:15(41)]
  08:20 (55): above. Resolves 08:15 and 08:10.
              result[08:15] = 08:20. result[08:10] = 08:20.
              08:20 itself above → None.  Stack: []
  08:25 (38): below. Push.              Stack: [08:25(38)]
  08:30 (60): above. Resolves 08:25.
              result[08:25] = 08:30.     Stack: []

Results:
  08:00 → 08:05 (next breach 5 min later)
  08:05 → None (already above)
  08:10 → 08:20 (10 min wait)
  08:15 → 08:20 (5 min wait)
  08:20 → None (already above)
  08:25 → 08:30 (5 min wait)
  08:30 → None (no future data)

7 data points, 7 pushes + 4 pops = 11 operations. O(n).
```
````

---

## 4th DE Scenario (Optional): Add if you determine Pattern 08 needs 4 DE scenarios for consistency with other patterns

Check how many DE scenarios other patterns have. If they all have 4, create a 4th scenario: `undo_redo_operations.py` and `undo_redo_operations.md` covering stack-based version tracking in data transformations (push state on transform, pop on rollback).

---

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== DE Scenario files ==="
ls patterns/08_stack/de_scenarios/*.py patterns/08_stack/de_scenarios/*.md 2>/dev/null

echo ""
echo "=== Run DE scenarios ==="
uv run python -m patterns.08_stack.de_scenarios.nested_validation
echo ""
uv run python -m patterns.08_stack.de_scenarios.expression_eval
echo ""
uv run python -m patterns.08_stack.de_scenarios.monotonic_time_series

echo ""
echo "=== Full Pattern 08 test suite ==="
uv run pytest patterns/08_stack/ -v --tb=short 2>&1 | tail -15

echo ""
echo "=== Pattern 08 completeness ==="
echo "Problems:"
ls patterns/08_stack/problems/*.md | wc -l
echo "(should be 6)"
echo "DE Scenarios:"
ls patterns/08_stack/de_scenarios/*.md 2>/dev/null | wc -l
echo "(should be 3 or 4)"
echo "Worked Examples:"
grep -rl "## Worked Example" patterns/08_stack/ | wc -l
echo "(should be 9-10: 6 problems + 3-4 DE scenarios)"
echo "Approach explanations:"
grep -c "📝 Explanation" patterns/08_stack/problems/*.md | awk -F: '{sum+=$2} END{print sum}'

echo ""
echo "=== Style check ==="
grep -r "—" patterns/08_stack/ && echo "❌ Em dashes found" || echo "✅ No em dashes"
grep -rn "## Visual Walkthrough" patterns/08_stack/ && echo "❌ Wrong section name" || echo "✅ Correct section names"
```
