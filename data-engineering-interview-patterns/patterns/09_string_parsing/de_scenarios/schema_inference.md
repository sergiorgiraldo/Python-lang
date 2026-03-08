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
