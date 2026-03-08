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
