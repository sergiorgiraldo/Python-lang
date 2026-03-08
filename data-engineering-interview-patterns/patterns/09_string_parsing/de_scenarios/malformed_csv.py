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
        'Alice,New York,"likes ""pizza"""\n'  # escaped quotes
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
