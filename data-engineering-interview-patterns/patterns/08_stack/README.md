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

### Scale characteristics

Stack operations (push/pop/peek) are O(1). The stack itself uses O(n) memory in the worst case (e.g., all opening brackets, no closers). For most problems, the stack size is bounded by something smaller than n.

| Problem type | Typical stack size | Memory at n=10M |
|---|---|---|
| Bracket matching | O(nesting depth), usually << n | Negligible |
| Expression evaluation | O(operands), usually << n | Negligible |
| Monotonic stack | O(n) worst case | ~80MB for indices |
| Next greater element | O(n) worst case | ~80MB for indices |

Stack algorithms are inherently sequential: each push/pop depends on the current state. They don't parallelize. This is usually fine because stack operations are fast and the data is processed in a single pass.

**Streaming context:** Stack-based algorithms work naturally on streams because they process elements left to right in a single pass. A bracket validator for streaming JSON doesn't need the full document in memory - just the stack of open brackets. In practice, streaming JSON parsers (like Python's ijson) use exactly this pattern. The memory is bounded by nesting depth, not document size.

**When stacks break at scale:** Recursive stack algorithms (DFS on deep graphs) can hit Python's recursion limit (~1000 by default). For very deep structures, convert to iterative with an explicit stack. This isn't about scale in the data-size sense but in the nesting-depth sense. A JSON document with 10K levels of nesting will crash recursive parsers.

### SQL equivalent

Stack operations don't have a direct SQL equivalent because SQL is set-based, not sequential. However, the problems stacks solve appear in SQL: bracket matching is structural validation (usually done outside SQL), expression evaluation is handled by the SQL parser itself and the monotonic stack's "next greater element" can be computed with a self-join or window function: `SELECT a.val, MIN(b.val) FROM t a JOIN t b ON b.idx > a.idx AND b.val > a.val GROUP BY a.idx, a.val`. The window function approach is less efficient than the stack algorithm. Recursive CTEs can simulate stack-based traversal for hierarchical data.

## Problems in This Section

| # | Problem | Difficulty | Key Concept |
|---|---|---|---|
| [20](https://leetcode.com/problems/valid-parentheses/) | [Valid Parentheses](problems/020_valid_parentheses.md) | Easy | Matching brackets with a stack |
| [155](https://leetcode.com/problems/min-stack/) | [Min Stack](problems/155_min_stack.md) | Medium | O(1) min alongside push/pop |
| [150](https://leetcode.com/problems/evaluate-reverse-polish-notation/) | [Evaluate RPN](problems/150_eval_rpn.md) | Medium | Postfix expression evaluation |
| [739](https://leetcode.com/problems/daily-temperatures/) | [Daily Temperatures](problems/739_daily_temperatures.md) | Medium | Monotonic decreasing stack |
| [853](https://leetcode.com/problems/car-fleet/) | [Car Fleet](problems/853_car_fleet.md) | Medium | Monotonic stack by arrival time |
| [84](https://leetcode.com/problems/largest-rectangle-in-histogram/) | [Largest Rectangle](problems/084_largest_rectangle.md) | Hard | Monotonic increasing stack |

## DE Scenarios

| Scenario | Stack Pattern | Real-World Use |
|---|---|---|
| [Nested Structure Validation](de_scenarios/nested_validation.md) | Matching | Validate JSON/XML in pipelines |
| [Expression Evaluation](de_scenarios/expression_eval.md) | Evaluation | Parse config expressions |
| [Monotonic Time Series](de_scenarios/monotonic_time_series.md) | Monotonic | Next-threshold analysis |
| [Undo/Redo Operations](de_scenarios/undo_redo_operations.md) | Push/Pop state | Version tracking in transforms |
