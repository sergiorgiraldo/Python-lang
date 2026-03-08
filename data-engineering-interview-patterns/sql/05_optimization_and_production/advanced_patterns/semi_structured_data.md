# Semi-Structured Data in SQL

JSON in SQL is increasingly common as APIs, event streams and log systems
produce nested data. Every major SQL engine has JSON support, but the syntax
varies significantly.

## Core Operations

### 1. Extract Scalar Values

Pull a single value out of a JSON document:

```sql
-- DuckDB: arrow operator (->>' for string, -> for JSON)
SELECT response_json->>'$.status' AS status FROM api_responses;

-- Equivalent function form
SELECT json_extract_string(response_json, '$.status') FROM api_responses;
```

### 2. Navigate Nested Objects

Access values deep in the JSON tree using dot-path notation:

```sql
-- DuckDB: dot-path in the JSON path string
SELECT response_json->>'$.data.user_id' AS user_id FROM api_responses;
```

### 3. Flatten/Unnest JSON Arrays

Convert a JSON array into rows. In DuckDB, cast to `JSON[]` then use `unnest`:

```sql
SELECT
    request_id,
    unnest(json_extract(response_json, '$.data.items')::JSON[]) AS item
FROM api_responses
WHERE response_json->>'$.status' = 'success';
```

Then extract fields from each array element:

```sql
SELECT
    request_id,
    CAST(item->>'$.id' AS INTEGER) AS item_id,
    CAST(item->>'$.price' AS DOUBLE) AS price
FROM (
    SELECT request_id,
           unnest(json_extract(response_json, '$.data.items')::JSON[]) AS item
    FROM api_responses
    WHERE response_json->>'$.status' = 'success'
) flattened;
```

### 4. Filter on JSON Fields

Use `->>` in WHERE clauses. The result is VARCHAR, so compare to strings:

```sql
WHERE response_json->>'$.status' = 'success'
```

For numeric comparisons, cast explicitly:

```sql
WHERE CAST(response_json->>'$.error_code' AS INTEGER) = 404
```

## Dialect Comparison

| Operation | DuckDB | BigQuery | Snowflake | Spark SQL | Postgres |
|---|---|---|---|---|---|
| Extract string | `->>'$.path'` | `JSON_EXTRACT_SCALAR(col, '$.path')` | `col:path::STRING` | `get_json_object(col, '$.path')` | `col->>'key'` |
| Extract JSON | `->'$.path'` | `JSON_EXTRACT(col, '$.path')` | `col:path` | `from_json(col, schema)` | `col->'key'` |
| Nested path | `->>'$.a.b.c'` | `JSON_EXTRACT_SCALAR(col, '$.a.b.c')` | `col:a.b.c` | `get_json_object(col, '$.a.b.c')` | `col#>>'{a,b,c}'` |
| Unnest array | `unnest(...)::JSON[]` | `UNNEST(JSON_EXTRACT_ARRAY(...))` | `LATERAL FLATTEN(col:arr)` | `explode(from_json(...))` | `jsonb_array_elements(col->'arr')` |
| Native type | JSON | JSON, STRUCT, ARRAY | VARIANT | StructType, ArrayType | jsonb |

### Snowflake Specifics

Snowflake uses the VARIANT type and colon notation:
```sql
-- Colon notation for path access
SELECT data:user:name::STRING FROM events;

-- LATERAL FLATTEN for arrays
SELECT e.request_id, f.value:id::INTEGER AS item_id
FROM events e, LATERAL FLATTEN(input => e.data:items) f;
```

### BigQuery Specifics

BigQuery has native STRUCT and ARRAY types alongside JSON:
```sql
-- JSON_EXTRACT_SCALAR for string values
SELECT JSON_EXTRACT_SCALAR(data, '$.user.name') FROM events;

-- UNNEST for arrays (native ARRAY type)
SELECT user_id, item
FROM events, UNNEST(items) AS item;

-- JSON_EXTRACT_ARRAY for JSON arrays
SELECT JSON_EXTRACT_SCALAR(item, '$.id')
FROM events, UNNEST(JSON_EXTRACT_ARRAY(data, '$.items')) AS item;
```

## At Scale

JSON parsing is expensive. For production pipelines:

1. **Parse once, materialize typed columns.** Do not re-parse the same JSON in
   multiple downstream queries.
2. **Use the "bronze to silver to gold" pattern** (or staging to intermediate
   to mart):
   - Bronze/staging: raw JSON as-is from the source
   - Silver/intermediate: extracted and typed columns, one row per entity
   - Gold/mart: aggregated, business-ready tables
3. **Schema validation**: use JSON schema or struct casting to catch malformed
   records early. Malformed JSON in a bronze table is fine. Malformed JSON
   leaking into a mart table is a data quality incident.
4. **Column pruning**: in columnar formats (Parquet, BigQuery), nested fields
   are stored as separate columns. Accessing `data.user.name` only reads that
   column, not the entire JSON blob. But the JSON must be stored in a
   structured format (STRUCT/ARRAY) for this to work. Raw JSON strings always
   require full parsing.

## Production Pattern: Landing Raw JSON

```sql
-- Stage 1: land raw JSON (bronze)
CREATE TABLE raw_api_events (
    event_id VARCHAR,
    received_at TIMESTAMP,
    payload JSON
);

-- Stage 2: extract typed columns (silver)
CREATE TABLE parsed_api_events AS
SELECT
    event_id,
    received_at,
    CAST(payload->>'$.user_id' AS INTEGER) AS user_id,
    payload->>'$.event_type' AS event_type,
    CAST(payload->>'$.amount' AS DECIMAL(10,2)) AS amount
FROM raw_api_events;

-- Stage 3: business aggregation (gold)
CREATE TABLE daily_user_summary AS
SELECT
    user_id,
    DATE_TRUNC('day', received_at) AS day,
    COUNT(*) AS event_count,
    SUM(amount) AS total_amount
FROM parsed_api_events
GROUP BY user_id, DATE_TRUNC('day', received_at);
```
