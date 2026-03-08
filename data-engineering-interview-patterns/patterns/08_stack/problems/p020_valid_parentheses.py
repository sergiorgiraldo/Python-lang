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
