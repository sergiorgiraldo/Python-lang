# CC Prompt: Create Pattern 09 String Parsing (Part 4 of 5)

## What This Prompt Does

Creates DE scenarios 1-2: Log Line Parsing and Malformed CSV Handling. These are the high-value scenarios that go beyond LeetCode into real DE work.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Every .md Worked Example starts with a prose paragraph
- DE scenarios include both .py (runnable with demo) and .md (documented)

---

## DE Scenario 1: Log Line Parsing

### `de_scenarios/log_parsing.py`

```python
"""
DE Scenario: Parse application log lines into structured records.

Real-world application: ingesting logs from applications, load balancers,
web servers and databases into a structured analytics table.

The challenge: log formats vary. Some lines match the expected format,
some don't. A robust parser handles known formats with regex and falls
back gracefully for unknown formats.

Run: uv run python -m patterns.09_string_parsing.de_scenarios.log_parsing
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class LogRecord:
    """Structured log record."""

    timestamp: str
    level: str
    logger: str
    message: str
    raw: str  # original line, always preserved


@dataclass
class ParseResult:
    """Result of parsing a log line."""

    record: Optional[LogRecord]
    parsed: bool
    pattern_used: str


# Common log patterns, ordered from most specific to most general
LOG_PATTERNS = [
    (
        "standard",
        re.compile(
            r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?)"
            r"\s+\[(?P<level>\w+)\]\s+"
            r"(?P<logger>[\w.]+)\s*[-:]\s*"
            r"(?P<message>.+)"
        ),
    ),
    (
        "brackets",
        re.compile(
            r"\[(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]"
            r"\s*\[(?P<level>\w+)\]\s*"
            r"\[(?P<logger>[\w.]+)\]\s*"
            r"(?P<message>.+)"
        ),
    ),
    (
        "syslog",
        re.compile(
            r"(?P<timestamp>\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})"
            r"\s+(?P<logger>\S+)"
            r"\s+(?P<level>\w+):\s*"
            r"(?P<message>.+)"
        ),
    ),
]


def parse_log_line(line: str) -> ParseResult:
    """
    Parse a single log line, trying multiple patterns.

    Tries patterns from most specific to most general.
    Falls back to a raw record if no pattern matches.
    """
    line = line.rstrip("\n")

    for name, pattern in LOG_PATTERNS:
        match = pattern.match(line)
        if match:
            groups = match.groupdict()
            record = LogRecord(
                timestamp=groups["timestamp"],
                level=groups["level"].upper(),
                logger=groups["logger"],
                message=groups["message"].strip(),
                raw=line,
            )
            return ParseResult(record=record, parsed=True, pattern_used=name)

    # Fallback: couldn't parse, preserve raw line
    return ParseResult(
        record=LogRecord(
            timestamp="",
            level="UNKNOWN",
            logger="",
            message=line,
            raw=line,
        ),
        parsed=False,
        pattern_used="fallback",
    )


def parse_log_batch(lines: list[str]) -> dict:
    """
    Parse a batch of log lines and return stats.

    In production, this would write to a structured table
    with a separate error/quarantine table for unparsed lines.
    """
    results = []
    stats = {"total": 0, "parsed": 0, "failed": 0, "by_pattern": {}}

    for line in lines:
        if not line.strip():
            continue

        stats["total"] += 1
        result = parse_log_line(line)
        results.append(result)

        if result.parsed:
            stats["parsed"] += 1
            stats["by_pattern"][result.pattern_used] = (
                stats["by_pattern"].get(result.pattern_used, 0) + 1
            )
        else:
            stats["failed"] += 1

    return {"records": results, "stats": stats}


if __name__ == "__main__":
    sample_logs = [
        '2024-01-15 08:23:45.123 [INFO] com.app.service - Request processed in 45ms',
        '2024-01-15 08:23:46 [ERROR] com.app.db - Connection timeout after 30s',
        '[2024-01-15 08:23:47] [WARN] [com.app.cache] Cache miss for key user:1234',
        'Jan 15 08:23:48 appserver INFO: Health check passed',
        'This line has no recognizable format at all',
        '2024-01-15 08:23:50.789 [DEBUG] com.app.auth: Token validated for user admin@corp.com',
    ]

    print("=== Log Line Parsing ===\n")

    batch = parse_log_batch(sample_logs)

    for result in batch["records"]:
        r = result.record
        status = "PARSED" if result.parsed else "FAILED"
        print(f"  [{status}] pattern={result.pattern_used}")
        print(f"    timestamp: {r.timestamp}")
        print(f"    level:     {r.level}")
        print(f"    logger:    {r.logger}")
        print(f"    message:   {r.message[:60]}")
        print()

    stats = batch["stats"]
    print(f"  Stats: {stats['parsed']}/{stats['total']} parsed, "
          f"{stats['failed']} failed")
    print(f"  Patterns used: {stats['by_pattern']}")
```

### `de_scenarios/log_parsing.md`

````markdown
# DE Scenario: Log Line Parsing

## Real-World Context

Application logs are one of the most common data sources in DE pipelines. They arrive in various formats (standard log4j, syslog, custom formats) and must be parsed into structured columns (timestamp, level, logger, message) for querying.

The challenge: format inconsistency. A single application might produce logs in different formats depending on the library, version or configuration. A robust parser tries multiple patterns and falls back gracefully rather than crashing on unexpected input.

## Worked Example

Multi-pattern parsing with fallback. The parser tries regex patterns from most specific to most general. If none match, it preserves the raw line (never lose data) and flags it for review. In production, parsed records go to the main table and unparsed records go to a quarantine table.

```
Input lines:
  1: "2024-01-15 08:23:45.123 [INFO] com.app.service - Request processed in 45ms"
  2: "[2024-01-15 08:23:47] [WARN] [com.app.cache] Cache miss for key user:1234"
  3: "This line has no recognizable format at all"

Line 1: try "standard" pattern
  Regex: timestamp=2024-01-15 08:23:45.123, level=INFO,
         logger=com.app.service, message=Request processed in 45ms
  Match. → LogRecord(timestamp="2024-01-15 08:23:45.123", level="INFO", ...)

Line 2: try "standard" pattern → no match (different bracket format)
  Try "brackets" pattern
  Regex: timestamp=2024-01-15 08:23:47, level=WARN,
         logger=com.app.cache, message=Cache miss for key user:1234
  Match. → LogRecord(...)

Line 3: try all patterns → no match
  Fallback. → LogRecord(timestamp="", level="UNKNOWN", message=raw line)
  Flag for review. Don't drop it.

Stats: 2/3 parsed (67%), 1 failed, patterns used: {standard: 1, brackets: 1}
```

## Key Design Decisions

1. **Try multiple patterns, not one mega-regex.** Easier to maintain and debug.
2. **Most specific first.** Avoids false matches from overly general patterns.
3. **Always preserve the raw line.** Even if parsing fails, the data isn't lost.
4. **Track parse stats.** If the failure rate spikes, something changed upstream.
5. **Named capture groups** (`(?P<name>...)`) make the extracted fields self-documenting.
````

---

## DE Scenario 2: Malformed CSV Handling

### `de_scenarios/malformed_csv.py`

```python
"""
DE Scenario: Handle malformed CSV files that break standard parsers.

Real-world application: processing vendor exports, legacy system dumps
and user-uploaded files where the CSV format is... creative.

The standard csv.reader handles RFC 4180 CSVs. Real data often deviates:
mixed quoting, embedded newlines, inconsistent delimiters, BOM characters,
null bytes, mixed encodings. This module handles the common edge cases.

Run: uv run python -m patterns.09_string_parsing.de_scenarios.malformed_csv
"""

import csv
import io
from dataclasses import dataclass, field
from typing import Iterator


@dataclass
class CSVParseResult:
    """Result of parsing a CSV file."""

    records: list[list[str]]
    errors: list[dict]
    stats: dict = field(default_factory=dict)


def parse_csv_robust(
    text: str,
    delimiter: str = ",",
    quote_char: str = '"',
    max_fields: int | None = None,
) -> CSVParseResult:
    """
    Parse a CSV string, handling common malformations.

    Handles:
    - BOM (byte order mark) at start of file
    - Mixed line endings (\\r\\n, \\n, \\r)
    - Embedded newlines within quoted fields
    - Unescaped quotes within fields
    - Inconsistent field counts (too many or too few)
    - Empty lines
    - Null bytes

    Returns parsed records + error log for malformed lines.
    """
    # Clean up common issues
    text = text.lstrip("\ufeff")  # remove BOM
    text = text.replace("\x00", "")  # remove null bytes
    text = text.replace("\r\n", "\n").replace("\r", "\n")  # normalize line endings

    records: list[list[str]] = []
    errors: list[dict] = []
    line_num = 0

    try:
        reader = csv.reader(
            io.StringIO(text),
            delimiter=delimiter,
            quotechar=quote_char,
        )
        for row in reader:
            line_num += 1
            if not any(field.strip() for field in row):
                continue  # skip blank lines

            if max_fields and len(row) > max_fields:
                errors.append({
                    "line": line_num,
                    "error": f"Too many fields: expected {max_fields}, got {len(row)}",
                    "raw": delimiter.join(row),
                })
                # Truncate to max_fields rather than dropping
                records.append(row[:max_fields])
            elif max_fields and len(row) < max_fields:
                errors.append({
                    "line": line_num,
                    "error": f"Too few fields: expected {max_fields}, got {len(row)}",
                    "raw": delimiter.join(row),
                })
                # Pad with empty strings
                records.append(row + [""] * (max_fields - len(row)))
            else:
                records.append(row)

    except csv.Error as e:
        errors.append({
            "line": line_num,
            "error": f"CSV parser error: {e}",
            "raw": "",
        })

    return CSVParseResult(
        records=records,
        errors=errors,
        stats={
            "total_records": len(records),
            "error_count": len(errors),
            "field_counts": _count_field_widths(records),
        },
    )


def parse_csv_manual(text: str, delimiter: str = ",") -> list[list[str]]:
    """
    Manual character-by-character CSV parser.

    Demonstrates the state machine approach for cases where
    Python's csv module can't handle the format.

    States: FIELD_START, UNQUOTED, QUOTED, QUOTE_IN_QUOTED
    """
    records: list[list[str]] = []
    current_record: list[str] = []
    current_field: list[str] = []

    STATE_FIELD_START = 0
    STATE_UNQUOTED = 1
    STATE_QUOTED = 2
    STATE_QUOTE_IN_QUOTED = 3

    state = STATE_FIELD_START
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    for char in text:
        if state == STATE_FIELD_START:
            if char == '"':
                state = STATE_QUOTED
            elif char == delimiter:
                current_record.append("")
            elif char == "\n":
                current_record.append("")
                if any(f for f in current_record):
                    records.append(current_record)
                current_record = []
            else:
                current_field.append(char)
                state = STATE_UNQUOTED

        elif state == STATE_UNQUOTED:
            if char == delimiter:
                current_record.append("".join(current_field))
                current_field = []
                state = STATE_FIELD_START
            elif char == "\n":
                current_record.append("".join(current_field))
                current_field = []
                if any(f for f in current_record):
                    records.append(current_record)
                current_record = []
                state = STATE_FIELD_START
            else:
                current_field.append(char)

        elif state == STATE_QUOTED:
            if char == '"':
                state = STATE_QUOTE_IN_QUOTED
            else:
                current_field.append(char)  # including newlines

        elif state == STATE_QUOTE_IN_QUOTED:
            if char == '"':
                # Escaped quote ("")
                current_field.append('"')
                state = STATE_QUOTED
            elif char == delimiter:
                current_record.append("".join(current_field))
                current_field = []
                state = STATE_FIELD_START
            elif char == "\n":
                current_record.append("".join(current_field))
                current_field = []
                if any(f for f in current_record):
                    records.append(current_record)
                current_record = []
                state = STATE_FIELD_START
            else:
                # Unescaped quote in middle of field (malformed)
                current_field.append('"')
                current_field.append(char)
                state = STATE_QUOTED

    # Flush remaining
    if current_field or current_record:
        current_record.append("".join(current_field))
        if any(f for f in current_record):
            records.append(current_record)

    return records


def _count_field_widths(records: list[list[str]]) -> dict[int, int]:
    """Count how many records have each field width."""
    counts: dict[int, int] = {}
    for record in records:
        width = len(record)
        counts[width] = counts.get(width, 0) + 1
    return counts


if __name__ == "__main__":
    print("=== Malformed CSV Handling ===\n")

    # Common edge cases in one file
    messy_csv = (
        '\ufeffname,city,note\n'  # BOM at start
        'Alice,New York,"likes ""pizza""\n'  # escaped quotes
        '"Bob ""B""",Chicago,normal\n'  # quotes in quoted field
        'Charlie,"San Francisco, CA",has comma\n'  # comma in quoted field
        'Diana,,"empty city"\n'  # empty field
        '"Eve\nNewline","Atlanta","embedded\nnewlines"\n'  # embedded newlines
        'Frank,Boston\n'  # too few fields
        'Grace,Denver,note,extra\n'  # too many fields
    )

    print("  Input (with edge cases):")
    for i, line in enumerate(messy_csv.split("\n")[:5]):
        print(f"    {i}: {repr(line)}")
    print(f"    ... ({len(messy_csv.split(chr(10)))} lines total)\n")

    result = parse_csv_robust(messy_csv, max_fields=3)

    print(f"  Parsed {result.stats['total_records']} records:")
    for i, record in enumerate(result.records):
        print(f"    {i}: {record}")

    if result.errors:
        print(f"\n  Errors ({len(result.errors)}):")
        for err in result.errors:
            print(f"    Line {err['line']}: {err['error']}")

    print(f"\n  Field width distribution: {result.stats['field_counts']}")

    print("\n=== Manual State Machine Parser ===\n")
    simple = 'a,"b,c",d\ne,"f""g",h\n'
    records = parse_csv_manual(simple)
    for r in records:
        print(f"  {r}")
```

### `de_scenarios/malformed_csv.md`

````markdown
# DE Scenario: Malformed CSV Handling

## Real-World Context

CSV is the most common data exchange format and also the most frequently broken. Vendor exports, legacy system dumps and user uploads routinely violate the RFC 4180 spec in creative ways: mixed quoting styles, embedded newlines, inconsistent delimiters, BOM characters, null bytes, and field counts that vary row to row.

Python's `csv.reader` handles well-formed CSVs. For the rest, you need a combination of preprocessing (cleaning known issues) and a fallback state-machine parser for cases the standard library can't handle.

## Worked Example

The robust approach: preprocess the text to fix known issues (BOM, null bytes, line endings), then use the standard csv.reader with error handling. Track field count inconsistencies separately - too many fields get truncated, too few get padded with empty strings. Never silently drop records.

```
Input (messy vendor export):
  Line 1: '\ufeffname,city,note'      ← BOM at start
  Line 2: 'Alice,New York,"likes ""pizza""'  ← escaped quotes
  Line 3: 'Charlie,"San Francisco, CA",has comma'  ← comma in quoted field
  Line 4: 'Frank,Boston'               ← only 2 fields (expected 3)
  Line 5: 'Grace,Denver,note,extra'    ← 4 fields (expected 3)

Preprocessing:
  Strip BOM (\ufeff) from start
  Remove null bytes (\x00)
  Normalize line endings to \n

Parse with csv.reader (max_fields=3):
  Line 1: ["name", "city", "note"] → header, 3 fields ✓
  Line 2: ["Alice", "New York", 'likes "pizza"'] → 3 fields ✓
           (csv.reader handles "" → " automatically)
  Line 3: ["Charlie", "San Francisco, CA", "has comma"] → 3 fields ✓
           (quoted field with comma handled correctly)
  Line 4: ["Frank", "Boston"] → 2 fields, expected 3
           Error logged. Pad to: ["Frank", "Boston", ""]
  Line 5: ["Grace", "Denver", "note", "extra"] → 4 fields, expected 3
           Error logged. Truncate to: ["Grace", "Denver", "note"]

Result: 5 records parsed, 2 with field count warnings.
No data lost. Errors logged for review.
```

## Key Design Decisions

1. **Preprocess then parse.** Fix the known issues (BOM, null bytes, line endings) before handing to csv.reader. Don't try to handle everything in one pass.
2. **Pad and truncate, don't drop.** Inconsistent field counts are warnings, not fatal errors. Pad short rows with empty strings. Truncate long rows. Log both.
3. **Track field width distribution.** If 99% of rows have 5 fields and 1% have 4, the 4-field rows are probably malformed. If it's 50/50, the format might have changed mid-file.
4. **Keep the raw line.** Always preserve the original data alongside the parsed result. You'll need it for debugging.
5. **State machine for the hard cases.** When csv.reader fails (e.g., unescaped quotes mid-field), a manual character-by-character parser with explicit state transitions can recover.
````

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== DE Scenario files ==="
ls patterns/09_string_parsing/de_scenarios/*.py patterns/09_string_parsing/de_scenarios/*.md 2>/dev/null

echo ""
echo "=== Run DE scenarios ==="
uv run python -m patterns.09_string_parsing.de_scenarios.log_parsing 2>&1 | tail -10
echo ""
uv run python -m patterns.09_string_parsing.de_scenarios.malformed_csv 2>&1 | tail -10
```
