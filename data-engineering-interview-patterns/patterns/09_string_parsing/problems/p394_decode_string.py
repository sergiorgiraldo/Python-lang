"""
LeetCode 394: Decode String

Pattern: String Parsing - Stack-based nested expansion
Difficulty: Medium
Time Complexity: O(n * max_expansion) where n is input length
Space Complexity: O(n) for the stack
"""


def decode_string(s: str) -> str:
    """
    Decode an encoded string like "3[a2[c]]" → "accaccacc".

    Rules:
    - k[encoded_string] means repeat encoded_string k times.
    - Nesting is allowed: the encoded_string can itself contain k[...].

    Stack approach: push the current string and repeat count when we
    see '['. Pop and build the result when we see ']'. The stack
    handles arbitrary nesting depth.
    """
    stack: list[tuple[str, int]] = []
    current = ""
    k = 0

    for char in s:
        if char.isdigit():
            k = k * 10 + int(char)  # handle multi-digit numbers
        elif char == "[":
            stack.append((current, k))
            current = ""
            k = 0
        elif char == "]":
            prev_string, repeat_count = stack.pop()
            current = prev_string + current * repeat_count
        else:
            current += char

    return current


def decode_string_recursive(s: str) -> str:
    """
    Recursive approach. Each '[' starts a recursive call,
    each ']' returns from it.
    """

    def helper(index: int) -> tuple[str, int]:
        result = ""
        k = 0

        while index < len(s):
            char = s[index]
            if char.isdigit():
                k = k * 10 + int(char)
                index += 1
            elif char == "[":
                decoded, index = helper(index + 1)
                result += decoded * k
                k = 0
            elif char == "]":
                return result, index + 1
            else:
                result += char
                index += 1

        return result, index

    result, _ = helper(0)
    return result
