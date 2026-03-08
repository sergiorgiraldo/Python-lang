# Evaluate Reverse Polish Notation (LeetCode #150)

🔗 [LeetCode 150: Evaluate Reverse Polish Notation](https://leetcode.com/problems/evaluate-reverse-polish-notation/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

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

**What the interviewer evaluates:** Operand order for subtraction and division (second-popped is the left operand) is where bugs hide. Division truncation toward zero (not floor division) is a Python-specific gotcha. Clean implementation with an operator dict shows good coding style. The interviewer likely has follow-up problems about infix evaluation or additional operators.

## DE Application

Config-driven pipelines sometimes use expression evaluation for computed columns: `"revenue", "cost", "-", "tax", "*"`. Stack-based evaluation handles these without building a full expression parser. Also useful for evaluating filter expressions in query builders.

## At Scale

The stack holds at most O(n/2) operands - roughly half the tokens. For 1M-token expressions, that's ~4MB. Expression evaluation is sequential and doesn't parallelize. At scale, the practical concern is precision: floating-point accumulation errors compound over long expressions. Financial calculations use decimal types, not floats. In data pipelines, expression evaluation appears in computed columns: config-driven transformations like `revenue - cost * tax_rate`. Template engines (Jinja in dbt, expression languages in Spark) parse and evaluate these using stack-based approaches internally.

## Related Problems

- [224. Basic Calculator](https://leetcode.com/problems/basic-calculator/) - Infix with parentheses (harder)
- [227. Basic Calculator II](https://leetcode.com/problems/basic-calculator-ii/) - Infix with precedence
