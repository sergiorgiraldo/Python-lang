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
