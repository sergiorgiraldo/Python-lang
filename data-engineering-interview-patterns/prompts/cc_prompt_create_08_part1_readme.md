# CC Prompt: Create Pattern 08 Stack (Part 1 of 5)

## What This Prompt Does

Creates the foundation for pattern 08: directory setup, conftest.py, template.py and a deep-teaching README.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- Create all files as specified. If files already exist, REPLACE them.
- NO Oxford commas, NO em dashes, NO exclamation points
- Python code: typed, documented, clean

---

## Directory Setup

```
patterns/08_stack/
├── README.md
├── __init__.py
├── template.py
├── problems/
│   ├── __init__.py
│   └── conftest.py
└── de_scenarios/
    └── __init__.py
```

Create any missing directories and `__init__.py` files.

## Create `problems/conftest.py`

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
```

## Create `template.py`

```python
"""
Stack Pattern Template

Three common stack patterns for interviews:

1. MATCHING/VALIDATION: Push openers, pop on closers, verify match
2. EXPRESSION EVALUATION: Push operands, pop and compute on operators
3. MONOTONIC STACK: Maintain sorted invariant for next-greater/smaller queries
"""


def matching_template(s: str) -> bool:
    """Template: bracket/tag matching."""
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


def monotonic_stack_template(nums: list[int]) -> list[int]:
    """Template: next greater element using a decreasing stack."""
    n = len(nums)
    result = [-1] * n
    stack: list[int] = []  # stores indices

    for i in range(n):
        while stack and nums[i] > nums[stack[-1]]:
            idx = stack.pop()
            result[idx] = nums[i]
        stack.append(i)

    return result
```

## Replace `README.md`

```markdown
# Stack Pattern

## What Is It?

### The basics

A stack is a last-in, first-out (LIFO) data structure. Think of a stack of plates: you add to the top and remove from the top. The most recently added item is always the first one out.

In Python, a regular `list` works as a stack:

```python
stack = []
stack.append(1)    # push: [1]
stack.append(2)    # push: [1, 2]
stack.append(3)    # push: [1, 2, 3]
stack.pop()        # returns 3, stack is [1, 2]
stack[-1]          # peek at top: 2 (without removing)
len(stack) == 0    # check if empty
```

Both `append()` and `pop()` are O(1). That's the entire data structure. No imports needed.

### Why stacks matter for interviews

Stacks solve problems where **the most recent context is what matters**. When you encounter a closing bracket, you need to check against the most recent opening bracket. When you evaluate an expression, the most recent operator or operand is what you process next. When you're looking for the "next warmer day," you care about the most recent unresolved temperature.

The pattern: push something onto the stack to "remember" it, pop it later when you find the thing that resolves it.

### The three stack patterns

**1. Matching/Validation**

Push opening tokens (brackets, tags, delimiters). When you see a closing token, pop the stack and verify it matches. If the stack is empty at the end, everything matched.

```python
for char in s:
    if char is an opener:
        stack.append(char)
    elif char is a closer:
        if stack is empty or stack.pop() doesn't match:
            return False
return len(stack) == 0
```

Examples: valid parentheses, HTML tag matching, JSON structure validation.

**2. Expression Evaluation**

Push operands (numbers). When you see an operator, pop the required operands, compute, push the result back. The stack handles operator precedence naturally in postfix (Reverse Polish) notation.

```python
for token in tokens:
    if token is a number:
        stack.append(number)
    else:  # operator
        b, a = stack.pop(), stack.pop()  # note: b first, then a
        stack.append(apply(a, token, b))
return stack[0]
```

Examples: evaluate RPN, basic calculator, config expression parsing.

**3. Monotonic Stack**

Maintain a stack where elements are always in sorted order (either increasing or decreasing). When a new element would break the order, pop everything it "beats" and resolve those popped elements. This pattern efficiently answers "next greater/smaller element" questions.

```python
for i in range(n):
    while stack and nums[i] > nums[stack[-1]]:
        idx = stack.pop()
        result[idx] = nums[i]  # nums[i] is the "next greater" for idx
    stack.append(i)
```

Examples: next warmer day, largest rectangle in histogram, stock span.

The key insight: each element is pushed once and popped at most once, so despite the nested loop, the total work is O(n).

### Connection to data engineering

Stacks appear in DE work more often than you'd expect:

- **JSON/XML validation:** Checking that nested structures are properly closed. A missing closing brace in a 500MB JSON file will break your pipeline.
- **Expression parsing:** Config-driven pipelines that evaluate expressions like `${env.DB_HOST}` or SQL template variables use stack-based parsing.
- **Log analysis:** Tracking nested function calls or transaction boundaries in log files. Each "begin" pushes context, each "end" pops it.
- **Time-series analysis:** "When does this metric next exceed a threshold?" is a monotonic stack problem. Finding the next spike after each data point.
- **Undo/redo systems:** Version tracking in data transformations. Each transform pushes state, rollback pops it.

### What the problems in this section use

| Problem | Stack pattern | What it models |
|---|---|---|
| Valid Parentheses | Matching | Bracket validation |
| Min Stack | Augmented stack | O(1) min tracking alongside normal operations |
| Eval RPN | Expression evaluation | Postfix expression computation |
| Daily Temperatures | Monotonic (decreasing) | "Next warmer day" for each position |
| Car Fleet | Monotonic (by arrival time) | Which cars catch up to the one ahead |
| Largest Rectangle | Monotonic (increasing) | Max area using each bar as height |

## When to Use It

**Recognition signals:**
- "Validate parentheses/brackets/tags..."
- "Evaluate an expression..."
- "Find the next greater/smaller element..."
- "Track a running minimum/maximum..."
- Anything with nested structure or last-in-first-out processing

## Visual Aid

```
Matching: "({[]})"

  Push '(' → stack: [(]
  Push '{' → stack: [(, {]
  Push '[' → stack: [(, {, []
  Pop  ']' → matches '['. stack: [(, {]
  Pop  '}' → matches '{'. stack: [(]
  Pop  ')' → matches '('. stack: []
  Stack empty at end → valid.

Monotonic stack (next warmer day):

  Temps: [73, 74, 75, 71, 69, 72, 76, 73]

  i=0: 73. Stack empty, push 0.             Stack: [0(73)]
  i=1: 74 > 73. Pop 0 → result[0]=1-0=1.   Stack: [1(74)]
  i=2: 75 > 74. Pop 1 → result[1]=2-1=1.   Stack: [2(75)]
  i=3: 71 < 75. Push 3.                     Stack: [2(75), 3(71)]
  i=4: 69 < 71. Push 4.                     Stack: [2(75), 3(71), 4(69)]
  i=5: 72 > 69. Pop 4 → result[4]=5-4=1.
       72 > 71. Pop 3 → result[3]=5-3=2.
       72 < 75. Push 5.                     Stack: [2(75), 5(72)]
  i=6: 76 > 72. Pop 5 → result[5]=6-5=1.
       76 > 75. Pop 2 → result[2]=6-2=4.   Stack: [6(76)]
  i=7: 73 < 76. Push 7.                     Stack: [6(76), 7(73)]

  Remaining in stack (6, 7) never found a warmer day → result stays 0.
  Result: [1, 1, 4, 2, 1, 1, 0, 0]

  Each element pushed once, popped at most once → O(n) total.
```

## Trade-offs

**When to use a stack vs other structures:**
- Stack vs queue: stack when most-recent matters (LIFO), queue when oldest matters (FIFO like BFS)
- Stack vs hash map: stack when order/nesting matters, hash map when you need O(1) lookup by key
- Stack vs heap: stack for sequential "next greater" problems, heap for global "kth largest" problems

**Monotonic stack vs brute force:**
- Brute force "next greater element" checks every future element for each position: O(n²)
- Monotonic stack resolves each element when its "answer" arrives: O(n) total
- The O(n) argument: each of n elements is pushed once and popped at most once = at most 2n operations

## Problems in This Section

| # | Problem | Difficulty | Key Concept |
|---|---|---|---|
| 20 | [Valid Parentheses](problems/020_valid_parentheses.md) | Easy | Matching brackets with a stack |
| 155 | [Min Stack](problems/155_min_stack.md) | Medium | O(1) min alongside push/pop |
| 150 | [Evaluate RPN](problems/150_eval_rpn.md) | Medium | Postfix expression evaluation |
| 739 | [Daily Temperatures](problems/739_daily_temperatures.md) | Medium | Monotonic decreasing stack |
| 853 | [Car Fleet](problems/853_car_fleet.md) | Medium | Monotonic stack by arrival time |
| 84 | [Largest Rectangle](problems/084_largest_rectangle.md) | Hard | Monotonic increasing stack |

## DE Scenarios

| Scenario | Stack Pattern | Real-World Use |
|---|---|---|
| [Nested Structure Validation](de_scenarios/nested_validation.md) | Matching | Validate JSON/XML in pipelines |
| [Expression Evaluation](de_scenarios/expression_eval.md) | Evaluation | Parse config expressions |
| [Monotonic Time Series](de_scenarios/monotonic_time_series.md) | Monotonic | Next-threshold analysis |
```

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== Files created ==="
find patterns/08_stack/ -type f | sort

echo ""
echo "=== README subsections ==="
grep "^### " patterns/08_stack/README.md

echo ""
echo "=== Key teaching sections ==="
for section in "The basics" "three stack patterns" "Matching" "Expression" "Monotonic" "Connection to data" "Visual Aid" "Trade-offs"; do
    grep -qi "$section" patterns/08_stack/README.md && echo "✅ $section" || echo "❌ $section"
done
```
