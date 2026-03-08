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
