# CC Prompt: Create Pattern 09 String Parsing (Part 5 of 5)

## What This Prompt Does

Creates DE scenarios 3-4: Schema Inference from JSON Samples and Regex Field Extraction.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Every .md Worked Example starts with a prose paragraph
- DE scenarios include both .py (runnable with demo) and .md (documented)

---

## DE Scenario 3: Schema Inference

### `de_scenarios/schema_inference.py`

```python
"""
DE Scenario: Infer schema from JSON samples.

Real-world application: automatically detecting column types, nullable
fields and nested structure when onboarding a new data source. Used by
tools like Spark's schema inference, dbt's source freshness and custom
pipeline bootstrap scripts.

Run: uv run python -m patterns.09_string_parsing.de_scenarios.schema_inference
"""

import json
import re
from dataclasses import dataclass
from typing import Any


@dataclass
class ColumnSchema:
    """Inferred schema for a single column."""

    name: str
    inferred_type: str  # string, integer, float, boolean, timestamp, object, array
    nullable: bool
    sample_values: list[Any]
    distinct_types_seen: set[str]


def infer_type(value: Any) -> str:
    """
    Infer the type of a single value.

    Order matters: check more specific types before general ones.
    A string that looks like a timestamp should be typed as timestamp,
    not string.
    """
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "float"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    if isinstance(value, str):
        # Check for timestamp patterns
        if re.match(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}", value):
            return "timestamp"
        # Check for date pattern
        if re.match(r"\d{4}-\d{2}-\d{2}$", value):
            return "date"
        # Check for numeric strings
        if re.match(r"^-?\d+$", value):
            return "integer_string"
        if re.match(r"^-?\d+\.\d+$", value):
            return "float_string"
        return "string"
    return "unknown"


def resolve_types(types_seen: set[str]) -> str:
    """
    Resolve multiple observed types into a single column type.

    Follows Spark-like widening rules:
    - integer + float → float
    - integer_string → integer (if all values match)
    - any type + null → nullable version of that type
    - incompatible types → string (safest fallback)
    """
    types_no_null = types_seen - {"null"}

    if not types_no_null:
        return "string"  # all nulls

    if len(types_no_null) == 1:
        t = types_no_null.pop()
        if t == "integer_string":
            return "integer"
        if t == "float_string":
            return "float"
        return t

    # Widening rules
    if types_no_null <= {"integer", "float", "integer_string", "float_string"}:
        return "float"

    if types_no_null <= {"integer", "integer_string"}:
        return "integer"

    # Incompatible types: fall back to string
    return "string"


def infer_schema(records: list[dict[str, Any]], sample_size: int = 5) -> list[ColumnSchema]:
    """
    Infer schema from a list of JSON records.

    Examines all records to determine type, nullable and collect samples.
    In production, you'd sample (e.g., first 1000 + random 1000) rather
    than scanning every record.
    """
    if not records:
        return []

    # Collect all keys across all records
    all_keys: list[str] = []
    seen_keys: set[str] = set()
    for record in records:
        for key in record:
            if key not in seen_keys:
                all_keys.append(key)
                seen_keys.add(key)

    schemas: list[ColumnSchema] = []

    for key in all_keys:
        types_seen: set[str] = set()
        samples: list[Any] = []
        null_count = 0
        total = len(records)

        for record in records:
            value = record.get(key)
            if value is None or key not in record:
                null_count += 1
                types_seen.add("null")
            else:
                t = infer_type(value)
                types_seen.add(t)
                if len(samples) < sample_size:
                    samples.append(value)

        resolved = resolve_types(types_seen)
        nullable = null_count > 0 or key not in records[0]  # missing from any record

        schemas.append(ColumnSchema(
            name=key,
            inferred_type=resolved,
            nullable=nullable,
            sample_values=samples,
            distinct_types_seen=types_seen - {"null"},
        ))

    return schemas


def schema_to_sql(schemas: list[ColumnSchema], table_name: str = "my_table") -> str:
    """Convert inferred schema to a CREATE TABLE statement."""
    type_map = {
        "string": "VARCHAR",
        "integer": "INTEGER",
        "float": "DOUBLE",
        "boolean": "BOOLEAN",
        "timestamp": "TIMESTAMP",
        "date": "DATE",
        "object": "JSON",
        "array": "JSON",
    }

    columns = []
    for col in schemas:
        sql_type = type_map.get(col.inferred_type, "VARCHAR")
        nullable = "" if col.nullable else " NOT NULL"
        columns.append(f"    {col.name} {sql_type}{nullable}")

    return f"CREATE TABLE {table_name} (\n" + ",\n".join(columns) + "\n);"


if __name__ == "__main__":
    print("=== Schema Inference ===\n")

    sample_records = [
        {
            "id": 1,
            "name": "Alice",
            "email": "alice@example.com",
            "created_at": "2024-01-15T08:30:00",
            "score": 95.5,
            "active": True,
            "tags": ["admin", "user"],
        },
        {
            "id": 2,
            "name": "Bob",
            "email": "bob@example.com",
            "created_at": "2024-01-16T10:00:00",
            "score": 87,
            "active": False,
            "tags": ["user"],
            "phone": "555-0102",
        },
        {
            "id": 3,
            "name": "Charlie",
            "email": None,
            "created_at": "2024-01-17T14:22:30",
            "score": 92.3,
            "active": True,
            "tags": [],
        },
    ]

    schemas = infer_schema(sample_records)

    for col in schemas:
        null_str = "NULLABLE" if col.nullable else "NOT NULL"
        print(f"  {col.name:15s} {col.inferred_type:12s} {null_str:10s} "
              f"types_seen={col.distinct_types_seen}")

    print(f"\n  SQL:\n{schema_to_sql(schemas, 'users')}")
```

### `de_scenarios/schema_inference.md`

````markdown
# DE Scenario: Schema Inference from JSON Samples

## Real-World Context

When onboarding a new data source, the first question is: what's the schema? For JSON data (API responses, event streams, document exports), the schema isn't declared - it's embedded in the data. Schema inference examines sample records to determine column names, types, nullable fields and nested structures.

This is what Spark does when you call `spark.read.json()` without specifying a schema. It samples the data, infers types and resolves conflicts. Understanding how this works helps you diagnose schema inference bugs and write better pipeline bootstrap scripts.

## Worked Example

For each field across all records, collect every type observed. Then resolve conflicting types using widening rules (integer + float → float, any type + null → nullable). Fields missing from some records are marked nullable.

```
Input records:
  {"id": 1, "name": "Alice", "score": 95.5, "active": true, "email": "alice@ex.com"}
  {"id": 2, "name": "Bob",   "score": 87,   "active": false, "phone": "555-0102"}
  {"id": 3, "name": "Charlie","score": 92.3, "active": true, "email": null}

Field-by-field analysis:

  id:     values=[1, 2, 3].       Types seen: {integer}. → INTEGER NOT NULL
  name:   values=["Alice", ...].  Types seen: {string}.  → VARCHAR NOT NULL
  score:  values=[95.5, 87, 92.3]. Types seen: {float, integer}.
          Resolve: integer + float → DOUBLE NOT NULL
  active: values=[true, false, true]. Types seen: {boolean}. → BOOLEAN NOT NULL
  email:  values=["alice@ex.com", missing, null].
          Types seen: {string, null}. Missing from record 2.
          → VARCHAR NULLABLE
  phone:  values=[missing, "555-0102", missing].
          Only in 1 of 3 records. Types seen: {string}.
          → VARCHAR NULLABLE

Generated SQL:
  CREATE TABLE users (
      id INTEGER NOT NULL,
      name VARCHAR NOT NULL,
      score DOUBLE NOT NULL,
      active BOOLEAN NOT NULL,
      email VARCHAR,
      phone VARCHAR
  );
```

## Key Design Decisions

1. **Check specific types before general.** `isinstance(value, bool)` must come before `isinstance(value, int)` because `bool` is a subclass of `int` in Python.
2. **Detect typed strings.** A string like "2024-01-15T08:30:00" is technically a string but should be typed as TIMESTAMP. Regex patterns catch common date/timestamp formats.
3. **Widening rules.** When a field has both integers and floats across records, widen to float. When types are truly incompatible (integer + boolean), fall back to string.
4. **Missing vs null.** A field that exists but is null is different from a field that's absent. Both make the column nullable, but the distinction matters for schema evolution.
````

---

## DE Scenario 4: Regex Field Extraction

### `de_scenarios/regex_extraction.py`

```python
"""
DE Scenario: Extract structured fields from unstructured text using regex.

Real-world application: parsing URLs, emails, IP addresses, phone numbers
and other structured data from free-text columns, log messages, or
user-generated content.

Run: uv run python -m patterns.09_string_parsing.de_scenarios.regex_extraction
"""

import re
from dataclasses import dataclass


@dataclass
class ExtractionResult:
    """Result of extracting fields from text."""

    original: str
    extracted: dict[str, list[str]]


# Compiled patterns for common field types
PATTERNS = {
    "email": re.compile(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    ),
    "ipv4": re.compile(
        r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}"
        r"(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b"
    ),
    "url": re.compile(
        r"https?://[^\s<>\"']+[^\s<>\"'.,;:!?)]"
    ),
    "phone_us": re.compile(
        r"(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}"
    ),
    "timestamp_iso": re.compile(
        r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?"
    ),
    "uuid": re.compile(
        r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
    ),
}


def extract_fields(text: str, field_types: list[str] | None = None) -> ExtractionResult:
    """
    Extract structured fields from unstructured text.

    Args:
        text: The text to extract from.
        field_types: Which field types to extract. None = all.
    """
    patterns_to_use = PATTERNS
    if field_types:
        patterns_to_use = {k: v for k, v in PATTERNS.items() if k in field_types}

    extracted: dict[str, list[str]] = {}
    for name, pattern in patterns_to_use.items():
        matches = pattern.findall(text)
        if matches:
            extracted[name] = matches

    return ExtractionResult(original=text, extracted=extracted)


def extract_with_named_groups(text: str, pattern: str) -> list[dict[str, str]]:
    """
    Extract fields using a regex with named capture groups.

    Named groups make the extraction self-documenting:
    (?P<timestamp>...) (?P<method>...) (?P<path>...) (?P<status>...)
    """
    compiled = re.compile(pattern)
    results = []
    for match in compiled.finditer(text):
        results.append(match.groupdict())
    return results


def build_extraction_pipeline(
    texts: list[str], field_types: list[str] | None = None
) -> list[ExtractionResult]:
    """
    Run extraction on a batch of texts.

    In production, this would be a UDF applied to a DataFrame column
    or a step in a streaming pipeline.
    """
    return [extract_fields(text, field_types) for text in texts]


if __name__ == "__main__":
    print("=== Regex Field Extraction ===\n")

    sample_texts = [
        "User admin@company.com logged in from 192.168.1.100 at 2024-01-15T08:30:00Z",
        "Error connecting to https://api.example.com/v2/users - timeout after 30s",
        "Contact support at support@example.com or call (555) 123-4567",
        "Transaction a1b2c3d4-e5f6-7890-abcd-ef1234567890 failed for user bob@test.org",
    ]

    for text in sample_texts:
        result = extract_fields(text)
        print(f"  Text: {text[:70]}...")
        for field_type, values in result.extracted.items():
            print(f"    {field_type}: {values}")
        print()

    print("=== Named Group Extraction (Access Log) ===\n")

    access_log = """
    192.168.1.1 - - [15/Jan/2024:08:30:00 +0000] "GET /api/users HTTP/1.1" 200 1234
    10.0.0.5 - admin [15/Jan/2024:08:30:01 +0000] "POST /api/login HTTP/1.1" 401 89
    192.168.1.2 - - [15/Jan/2024:08:30:02 +0000] "GET /api/health HTTP/1.1" 200 15
    """

    pattern = (
        r'(?P<ip>\d+\.\d+\.\d+\.\d+)\s+-\s+(?P<user>\S+)\s+'
        r'\[(?P<timestamp>[^\]]+)\]\s+'
        r'"(?P<method>\w+)\s+(?P<path>\S+)\s+\S+"\s+'
        r'(?P<status>\d+)\s+(?P<bytes>\d+)'
    )

    records = extract_with_named_groups(access_log, pattern)
    for r in records:
        print(f"  {r['ip']:15s} {r['method']:6s} {r['path']:20s} → {r['status']}")
```

### `de_scenarios/regex_extraction.md`

````markdown
# DE Scenario: Regex Field Extraction

## Real-World Context

Unstructured text columns are everywhere in data: log messages, user comments, support tickets, email bodies. Extracting structured fields (emails, IPs, URLs, timestamps) from these columns is a core DE task. Regex is the right tool when the data has consistent patterns but isn't formally structured.

The key principle: compile patterns once, apply them many times. Pre-compiled regex patterns are significantly faster than re-compiling per row.

## Worked Example

Apply a library of pre-compiled regex patterns to each text value. Each pattern targets a specific field type (email, IP, URL, etc.). The extraction runs independently for each type - a single text might yield an email, an IP and a timestamp.

```
Input: "User admin@company.com logged in from 192.168.1.100 at 2024-01-15T08:30:00Z"

Apply patterns:
  email:         admin@company.com matches [a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}
  ipv4:          192.168.1.100 matches \b(?:(?:25[0-5]|...)\.){3}...\b
  timestamp_iso: 2024-01-15T08:30:00Z matches \d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}...
  url:           no match
  phone:         no match
  uuid:          no match

Extracted: {
    "email": ["admin@company.com"],
    "ipv4": ["192.168.1.100"],
    "timestamp_iso": ["2024-01-15T08:30:00Z"]
}

For a batch of 1M rows, the compiled patterns run in a single pass
per pattern. Pre-compilation avoids re-parsing the regex for each row.
```

## Key Design Decisions

1. **Pre-compile patterns.** `re.compile()` once at module level, not per row. The compilation cost is significant for complex patterns.
2. **Named capture groups for complex formats.** `(?P<ip>...)` makes the extracted fields self-documenting. Essential when the extraction is part of a pipeline that others maintain.
3. **Keep it simple.** Email regex doesn't need to handle every RFC 5322 edge case. Match the 99% case and quarantine the rest.
4. **Return all matches, not just the first.** A text might contain multiple emails or IPs. Use `findall` or `finditer`, not `search`.
5. **Separate extraction from validation.** Extract with regex, then validate the extracted values (is this IP in a valid range? Is this email domain active?).
````

---

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== DE Scenario files ==="
ls patterns/09_string_parsing/de_scenarios/*.py patterns/09_string_parsing/de_scenarios/*.md 2>/dev/null

echo ""
echo "=== Run DE scenarios ==="
uv run python -m patterns.09_string_parsing.de_scenarios.schema_inference 2>&1 | tail -10
echo ""
uv run python -m patterns.09_string_parsing.de_scenarios.regex_extraction 2>&1 | tail -10

echo ""
echo "=== Full Pattern 09 test suite ==="
uv run pytest patterns/09_string_parsing/ -v --tb=short 2>&1 | tail -20

echo ""
echo "=== Pattern 09 completeness ==="
echo "Problems:"
ls patterns/09_string_parsing/problems/*.md 2>/dev/null | wc -l
echo "(should be 4)"
echo "DE Scenarios:"
ls patterns/09_string_parsing/de_scenarios/*.md 2>/dev/null | wc -l
echo "(should be 4)"
echo "Worked Examples:"
grep -rl "## Worked Example" patterns/09_string_parsing/ | wc -l
echo "(should be 8: 4 problems + 4 DE scenarios)"

echo ""
echo "=== Style check ==="
grep -r "—" patterns/09_string_parsing/ && echo "❌ Em dashes found" || echo "✅ No em dashes"
grep -rn "## Visual Walkthrough" patterns/09_string_parsing/ && echo "❌ Wrong section name" || echo "✅ Correct section names"
```
