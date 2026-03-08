"""
LeetCode 722: Remove Comments

Pattern: String Parsing - State machine
Difficulty: Medium
Time Complexity: O(n) where n is total characters
Space Complexity: O(n) for the output
"""


def remove_comments(source: list[str]) -> list[str]:
    """
    Remove C-style comments from source code.

    Two types of comments:
    - Line comment "//": ignore everything from // to end of line
    - Block comment "/* ... */": ignore everything between, can span lines

    Uses a state machine with two states:
    - in_block=False: normal mode, output characters
    - in_block=True: inside a block comment, skip characters

    Process character by character, looking ahead one character
    for "//" and "/*" and "*/" sequences.
    """
    result: list[str] = []
    current_line: list[str] = []
    in_block = False

    for line in source:
        i = 0
        while i < len(line):
            if in_block:
                # Looking for end of block comment
                if i + 1 < len(line) and line[i : i + 2] == "*/":
                    in_block = False
                    i += 2
                else:
                    i += 1
            else:
                if i + 1 < len(line) and line[i : i + 2] == "//":
                    # Line comment: skip rest of line
                    break
                elif i + 1 < len(line) and line[i : i + 2] == "/*":
                    # Block comment: enter block state
                    in_block = True
                    i += 2
                else:
                    current_line.append(line[i])
                    i += 1

        # Only add the line if we're not in a block comment
        # and the line has content
        if not in_block and current_line:
            result.append("".join(current_line))
            current_line = []

    return result
