# CC Prompt: Create Pattern 09 String Parsing (Part 1 of 5)

## What This Prompt Does

Creates the foundation for pattern 09: replaces the existing skeleton README, creates conftest.py, template.py, and ensures directory structure is complete.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- Replace existing README.md (it's a placeholder with no teaching content)
- Create missing files. If files exist, REPLACE them.
- NO Oxford commas, NO em dashes, NO exclamation points
- Python code: typed, documented, clean

---

## Directory Setup

Ensure this structure exists (create any missing directories and `__init__.py` files):

```
patterns/09_string_parsing/
├── README.md
├── __init__.py
├── template.py
├── problems/
│   ├── __init__.py
│   └── conftest.py
└── de_scenarios/
    └── __init__.py
```

## Create `problems/conftest.py`

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
```

## Create `template.py`

```python
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
```

## Replace `README.md`

Replace the existing README.md entirely with:

```markdown
# String Parsing Pattern

## What Is It?

### The basics

String parsing is the process of extracting structured information from unstructured or semi-structured text. In Python, this ranges from simple `str.split()` calls to complex state machines that track context as they walk through each character.

Unlike the algorithmic patterns (hash maps, binary search, etc.), string parsing doesn't have one core data structure. Instead, it's a toolkit of techniques:

```python
# Level 1: Split and strip
fields = line.split(",")
name = fields[0].strip()

# Level 2: Regex extraction
match = re.search(r'(\d{4}-\d{2}-\d{2}) (\w+): (.+)', line)
timestamp, level, message = match.groups()

# Level 3: Character-by-character with state
for char in text:
    if state == "normal" and char == '"':
        state = "quoted"
    elif state == "quoted" and char == '"':
        state = "normal"
    # ... handle each character based on current state

# Level 4: Stack-based for nested structures
for char in text:
    if char == '{':
        stack.append(current_object)
    elif char == '}':
        completed = stack.pop()
```

Each level handles progressively more complex input. Simple delimited data needs Level 1. Log files with known formats need Level 2. Data with quoting, escaping or nesting needs Levels 3-4.

### Why parsing matters more for DEs than SWEs

Most software engineers deal with well-structured data: JSON from APIs, protocol buffers, typed database results. Data engineers deal with whatever arrives: malformed CSVs with embedded delimiters, log files from systems you don't control, vendor exports with inconsistent quoting, semi-structured JSON with schema drift.

The ability to parse messy data reliably and efficiently is a core DE skill. It's not glamorous, but a single unhandled edge case (a comma inside a quoted field, a newline in a JSON string, a null byte in a log line) can corrupt millions of rows.

### The four parsing approaches

**1. Split/Join (Level 1)**
Use when: data has consistent delimiters and no quoting/escaping.

`line.split(",")` handles simple CSVs. `"|".join(fields)` reconstructs them. Fast (C implementation in CPython) and readable. Falls apart when fields contain the delimiter.

**2. Regex (Level 2)**
Use when: data has a known format and you need to extract specific fields.

Regular expressions are powerful for extraction but dangerous for parsing complex grammars. They handle log lines, URLs, timestamps and email addresses well. They handle nested structures (JSON, XML, HTML) poorly. The rule of thumb: if your regex needs lookahead/lookbehind or has more than 3 capture groups, consider a different approach.

```python
# Good regex use: extract fields from a known log format
pattern = r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[(?P<level>\w+)\] (?P<message>.+)'

# Bad regex use: parse nested JSON
# Don't. Use json.loads() or a proper parser.
```

**3. Character-by-character with state (Level 3)**
Use when: data has quoting, escaping or context-dependent delimiters.

Walk through each character, maintaining state (am I inside quotes? Did I just see a backslash?). This is how CSV parsers actually work internally. More code than regex but handles edge cases that regex can't.

**4. Stack-based parsing (Level 4)**
Use when: data has nesting (brackets, tags, nested JSON).

Same stack mechanics as Pattern 08 but applied to parsing rather than validation. Push context when entering a nested structure, pop when leaving. This is how JSON parsers and XML parsers work internally.

### Connection to data engineering

Parsing shows up in almost every pipeline:

- **Ingestion:** Raw files arrive in CSV, JSON, XML, log formats or proprietary exports. Parsing is the first transformation step.
- **Data quality:** Detecting malformed records requires understanding the expected format well enough to identify violations.
- **Schema inference:** Examining sample data to determine column types, nullable fields and nested structure requires parsing.
- **Log analysis:** Extracting metrics from application logs, audit trails and system events.
- **CDC parsing:** Change data capture events from databases arrive as structured-but-complex payloads that need field extraction.

### What the problems in this section cover

| Problem | Parsing technique | What it models |
|---|---|---|
| Encode/Decode Strings | Delimiter design + length prefixing | Data serialization |
| Decode String | Stack-based nested expansion | Template/config expansion |
| Remove Comments | State machine (normal/string/comment) | Code/config preprocessing |
| Validate IP Address | Structured validation with rules | Input validation |

| DE Scenario | Parsing technique | What it models |
|---|---|---|
| Log line parsing | Regex + fallback | Ingestion from mixed-format logs |
| Malformed CSV handling | Character-by-character with state | Handling real-world dirty data |
| Schema inference | Type detection + sampling | Automated pipeline setup |
| Regex field extraction | Named capture groups | Unstructured text to columns |

## When to Use It

**Recognition signals in interviews:**
- "Parse this string..."
- "Extract fields from..."
- "Handle escaped/quoted characters..."
- "Validate this format..."
- Anything involving nested or structured text

**Recognition signals in DE work:**
- Raw file ingestion with inconsistent formats
- Log analysis and metric extraction
- Data validation before loading
- Schema detection for new data sources

## Visual Aid

```
State machine for parsing code with comments:

  Input: "int x = 1; // comment\nint y = 2;"

  State: NORMAL
    'i' → output 'i'    (normal character)
    'n' → output 'n'
    't' → output 't'
    ' ' → output ' '
    ...
    ';' → output ';'
    ' ' → output ' '
    '/' → peek ahead...
    '/' → it's "//" → switch to LINE_COMMENT state

  State: LINE_COMMENT
    'c' → skip           (inside comment, ignore everything)
    'o' → skip
    ...
    '\n' → switch back to NORMAL, output '\n'

  State: NORMAL (again)
    'i' → output 'i'
    ...

  Output: "int x = 1; \nint y = 2;"

  For block comments (/* ... */), add a BLOCK_COMMENT state that
  only exits when it sees "*/". The state machine handles all
  combinations cleanly.
```

## Trade-offs

**When to use each parsing approach:**
- `str.split()` vs regex: split is 5-10x faster for simple delimiters. Use regex only when split can't express the pattern.
- Regex vs state machine: regex is more concise for flat patterns. State machines handle context and nesting that regex can't.
- Custom parser vs library: Use `csv.reader`, `json.loads`, `xml.etree` when the format is standard. Write custom parsers only when the data deviates from the standard (which in DE, it often does).
- Strict vs lenient parsing: strict parsing rejects malformed input (safe but loses data). Lenient parsing attempts recovery (keeps more data but risks corruption). In pipelines, parse leniently but log everything you had to fix.

## Problems in This Section

| # | Problem | Difficulty | Key Concept |
|---|---|---|---|
| 271 | [Encode and Decode Strings](problems/271_encode_decode_strings.md) | Medium | Length-prefix serialization |
| 394 | [Decode String](problems/394_decode_string.md) | Medium | Stack-based nested expansion |
| 722 | [Remove Comments](problems/722_remove_comments.md) | Medium | State machine parsing |
| 468 | [Validate IP Address](problems/468_validate_ip_address.md) | Medium | Structured validation |

## DE Scenarios

| Scenario | Parsing Technique | Real-World Use |
|---|---|---|
| [Log Line Parsing](de_scenarios/log_parsing.md) | Regex + fallback | Extract fields from application logs |
| [Malformed CSV Handling](de_scenarios/malformed_csv.md) | Char-by-char with state | Handle real-world dirty CSV files |
| [Schema Inference](de_scenarios/schema_inference.md) | Type detection + sampling | Auto-detect column types from samples |
| [Regex Field Extraction](de_scenarios/regex_extraction.md) | Named capture groups | Parse URLs, emails, IPs from text |
```

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== Files created ==="
find patterns/09_string_parsing/ -type f | sort

echo ""
echo "=== README subsections ==="
grep "^### " patterns/09_string_parsing/README.md

echo ""
echo "=== Key teaching sections ==="
for section in "The basics" "four parsing" "Split" "Regex" "Character-by-character" "Stack-based" "Connection to data" "Visual Aid" "Trade-offs"; do
    grep -qi "$section" patterns/09_string_parsing/README.md && echo "✅ $section" || echo "❌ $section"
done
```
