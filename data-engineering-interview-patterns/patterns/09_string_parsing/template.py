"""
String Parsing Pattern Template

Four common string parsing approaches for interviews and DE work:

1. CHARACTER-BY-CHARACTER with state tracking
2. SPLIT/JOIN for delimiter-based parsing
3. REGEX for pattern extraction
4. STACK-BASED for nested structures
"""

import re
from typing import Any


def char_by_char_template(s: str) -> list[str]:
    """
    Template: parse a string character by character with state.

    Useful when delimiters aren't enough (e.g., quoted CSV fields,
    comments in code, escape sequences).
    """
    tokens: list[str] = []
    current: list[str] = []
    in_quotes = False

    for char in s:
        if char == '"':
            in_quotes = not in_quotes
        elif char == "," and not in_quotes:
            tokens.append("".join(current))
            current = []
        else:
            current.append(char)

    tokens.append("".join(current))  # don't forget the last token
    return tokens


def regex_extraction_template(text: str, pattern: str) -> list[dict[str, str]]:
    """
    Template: extract structured data using named capture groups.

    Named groups (?P<name>...) make the extracted data self-documenting.
    """
    results = []
    for match in re.finditer(pattern, text):
        results.append(match.groupdict())
    return results


def state_machine_template(s: str) -> Any:
    """
    Template: finite state machine for complex parsing.

    States transition based on the current character. Each state
    has its own rules for what to do with the character.
    """
    STATE_NORMAL = "normal"
    STATE_STRING = "string"
    STATE_ESCAPE = "escape"

    state = STATE_NORMAL
    result: list[str] = []

    for char in s:
        if state == STATE_NORMAL:
            if char == '"':
                state = STATE_STRING
            else:
                result.append(char)
        elif state == STATE_STRING:
            if char == "\\":
                state = STATE_ESCAPE
            elif char == '"':
                state = STATE_NORMAL
            else:
                result.append(char)
        elif state == STATE_ESCAPE:
            result.append(char)
            state = STATE_STRING

    return "".join(result)
