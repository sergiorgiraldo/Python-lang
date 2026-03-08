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
