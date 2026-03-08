# SQL Dialect Comparison

Feature availability across DuckDB, BigQuery, Snowflake, Spark SQL and Postgres.
Knowing dialect differences is critical for interviews: the target company's
engine determines which patterns are available.

## Feature Matrix

| Feature | DuckDB | BigQuery | Snowflake | Spark SQL | Postgres |
|---|---|---|---|---|---|
| QUALIFY | Yes | Yes | Yes | No (use subquery) | No (use subquery) |
| GROUPING SETS | Yes | Yes | Yes | Yes | Yes |
| ROLLUP / CUBE | Yes | Yes | Yes | Yes | Yes |
| PIVOT / UNPIVOT | Yes | Yes | Yes | Yes (pivot()) | crosstab extension |
| Recursive CTEs | Yes | Yes (500 iter limit) | Yes | No | Yes |
| LATERAL JOIN | Yes | No (use UNNEST) | Yes | No (use explode) | Yes |
| MERGE | Yes | Yes | Yes | Yes (Delta Lake) | INSERT ON CONFLICT |
| APPROX_COUNT_DISTINCT | Yes | Yes | Yes | Yes | HyperLogLog extension |
| Array / Struct types | Yes | Yes | Yes (VARIANT) | Yes | Yes (arrays, composite) |
| JSON functions | Yes (json_extract) | JSON_EXTRACT_SCALAR | PARSE_JSON, : notation | from_json, get_json_object | jsonb, ->>, #>> |
| Window frame GROUPS | Yes | No | No | No | Yes |
| FILTER clause on agg | Yes | No | No | No | Yes |
| EXPLAIN | Yes | No (Query Details UI) | No (Query Profile UI) | Yes (explain) | Yes (EXPLAIN ANALYZE) |
| TABLESAMPLE | Yes | Yes | Yes | Yes | Yes |
| EXCLUDE columns | Yes | No | Yes (partial) | No | No |
| LIST_AGG / STRING_AGG | string_agg | STRING_AGG | LISTAGG | collect_list + concat_ws | string_agg |
| ASOF JOIN | Yes | No | Yes | No | No |

## Feature Details

### 1. QUALIFY

Filters rows after window function evaluation, the same way HAVING filters
after GROUP BY.

**DuckDB / BigQuery / Snowflake:**
```sql
SELECT user_id, event_time, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY event_time DESC) AS rn
FROM events
QUALIFY rn = 1;
```

**Postgres / Spark SQL (workaround):**
```sql
SELECT * FROM (
    SELECT user_id, event_time,
           ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY event_time DESC) AS rn
    FROM events
) t
WHERE rn = 1;
```

**Interview relevance:** QUALIFY saves a subquery for window function filters.
If the target company uses BigQuery or Snowflake, use it. Demonstrates you
know the engine. If Postgres, show the subquery workaround.

---

### 2. MERGE (Upsert)

The standard pattern for incremental loads: insert new rows, update existing ones.

**BigQuery / Snowflake:**
```sql
MERGE INTO target t
USING source s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET t.name = s.name, t.updated_at = s.updated_at
WHEN NOT MATCHED THEN INSERT (id, name, updated_at) VALUES (s.id, s.name, s.updated_at);
```

**DuckDB:**
```sql
-- DuckDB supports MERGE with similar syntax
MERGE INTO target t
USING source s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET name = s.name
WHEN NOT MATCHED THEN INSERT VALUES (s.id, s.name);
```

**Spark SQL (Delta Lake only):**
```sql
MERGE INTO target t
USING source s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

**Postgres:**
```sql
INSERT INTO target (id, name, updated_at)
SELECT id, name, updated_at FROM source
ON CONFLICT (id)
DO UPDATE SET name = EXCLUDED.name, updated_at = EXCLUDED.updated_at;
```

**Interview relevance:** MERGE is the core pattern for incremental/upsert loads
in data engineering. Know the syntax for your target engine. Postgres uses
INSERT ON CONFLICT which has different semantics (single-table, no DELETE clause).

---

### 3. APPROX_COUNT_DISTINCT

HyperLogLog-based approximate distinct count. Trades accuracy for speed.

**DuckDB:**
```sql
SELECT approx_count_distinct(user_id) FROM events;
```

**BigQuery:**
```sql
SELECT APPROX_COUNT_DISTINCT(user_id) FROM events;
```

**Snowflake:**
```sql
SELECT APPROX_COUNT_DISTINCT(user_id) FROM events;
-- Also: HLL() for the raw HyperLogLog sketch
```

**Spark SQL:**
```sql
SELECT approx_count_distinct(user_id) FROM events;
```

**Postgres:**
```sql
-- Requires the hll extension
CREATE EXTENSION IF NOT EXISTS hll;
SELECT hll_cardinality(hll_add_agg(hll_hash_integer(user_id))) FROM events;
```

**Interview relevance:** demonstrates you understand the exact vs approximate
tradeoff. At scale, COUNT(DISTINCT) on billions of rows is expensive.
APPROX_COUNT_DISTINCT is 1-2% error with much less memory and computation.

---

### 4. Recursive CTEs

Traverse hierarchies, generate series, process graph structures.

**DuckDB / Postgres / BigQuery / Snowflake:**
```sql
WITH RECURSIVE org_tree AS (
    -- Base case: root nodes
    SELECT id, name, manager_id, 1 AS level
    FROM employees WHERE manager_id IS NULL
    UNION ALL
    -- Recursive step
    SELECT e.id, e.name, e.manager_id, t.level + 1
    FROM employees e
    JOIN org_tree t ON e.manager_id = t.id
)
SELECT * FROM org_tree;
```

**BigQuery note:** limited to 500 iterations by default. Adjust with
`max_recursion_depth` option.

**Spark SQL:** recursive CTEs are not supported. Use DataFrame operations:
```python
# PySpark approach
current = spark.sql("SELECT * FROM employees WHERE manager_id IS NULL")
result = current
while current.count() > 0:
    current = spark.sql(f"""
        SELECT e.* FROM employees e
        JOIN current_level c ON e.manager_id = c.id
    """)
    result = result.union(current)
```

---

### 5. LATERAL JOIN

Allows the right side of the join to reference columns from the left side.

**DuckDB / Postgres / Snowflake:**
```sql
SELECT d.name, e.emp_name, e.salary
FROM departments d,
LATERAL (
    SELECT name AS emp_name, salary
    FROM employees
    WHERE department_id = d.id
    ORDER BY salary DESC
    LIMIT 3
) e;
```

**BigQuery (UNNEST alternative):**
```sql
-- For flattening arrays
SELECT user_id, item
FROM users, UNNEST(purchase_items) AS item;

-- For top-N per group, use window functions instead
SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rn
    FROM employees
) WHERE rn <= 3;
```

**Spark SQL (explode alternative):**
```sql
SELECT user_id, explode(purchase_items) AS item
FROM users;
```

---

### 6. PIVOT / UNPIVOT

Transform rows to columns (PIVOT) or columns to rows (UNPIVOT).

**DuckDB:**
```sql
PIVOT sales ON product USING SUM(revenue) GROUP BY region;
```

**BigQuery:**
```sql
SELECT * FROM sales
PIVOT (SUM(revenue) FOR product IN ('Widget', 'Gadget'));
```

**Snowflake:**
```sql
SELECT * FROM sales
PIVOT (SUM(revenue) FOR product IN ('Widget', 'Gadget'));
```

**Spark SQL:**
```python
df.groupBy("region").pivot("product").sum("revenue")
```

**Postgres (crosstab):**
```sql
-- Requires tablefunc extension
SELECT * FROM crosstab(
    'SELECT region, product, SUM(revenue) FROM sales GROUP BY 1, 2 ORDER BY 1, 2',
    $$VALUES ('Widget'), ('Gadget')$$
) AS ct(region TEXT, widget BIGINT, gadget BIGINT);
```

---

### 7. JSON / Semi-Structured Data

**DuckDB:**
```sql
SELECT json_extract_string(data, '$.user.name') FROM events;
-- Or arrow syntax:
SELECT data->>'$.user.name' FROM events;
```

**BigQuery:**
```sql
SELECT JSON_EXTRACT_SCALAR(data, '$.user.name') FROM events;
```

**Snowflake:**
```sql
-- Colon notation on VARIANT columns
SELECT data:user:name::STRING FROM events;
-- Or PARSE_JSON for string columns
SELECT PARSE_JSON(data):user:name::STRING FROM events;
```

**Spark SQL:**
```sql
SELECT get_json_object(data, '$.user.name') FROM events;
-- Or with schema:
SELECT from_json(data, 'struct<user:struct<name:string>>').user.name FROM events;
```

**Postgres:**
```sql
SELECT data->>'name' FROM events;           -- text extraction
SELECT data #>> '{user,name}' FROM events;  -- nested path
```

---

### 8. GROUPING SETS / ROLLUP / CUBE

Syntax is identical across all major engines:
```sql
SELECT region, product, SUM(revenue)
FROM sales
GROUP BY GROUPING SETS ((region, product), (region), ());
```

Supported in DuckDB, BigQuery, Snowflake, Spark SQL and Postgres. No
workaround needed since it is universally available.

---

### 9. FILTER Clause on Aggregates

**DuckDB / Postgres:**
```sql
SELECT
    COUNT(*) FILTER (WHERE status = 'active') AS active_count,
    COUNT(*) FILTER (WHERE status = 'inactive') AS inactive_count
FROM users;
```

**All other engines (workaround):**
```sql
SELECT
    COUNT(CASE WHEN status = 'active' THEN 1 END) AS active_count,
    COUNT(CASE WHEN status = 'inactive' THEN 1 END) AS inactive_count
FROM users;
```

---

### 10. ASOF JOIN

Join on the closest matching timestamp (no exact match required).

**DuckDB:**
```sql
SELECT * FROM trades
ASOF JOIN quotes ON trades.symbol = quotes.symbol
    AND trades.trade_time >= quotes.quote_time;
```

**Snowflake:**
```sql
SELECT * FROM trades
ASOF JOIN quotes
    MATCH_CONDITION (trades.trade_time >= quotes.quote_time)
    ON trades.symbol = quotes.symbol;
```

**All others:** use a window function or LATERAL JOIN with ORDER BY + LIMIT 1
to find the closest preceding record.

---

## Top 5 Interview-Critical Features

1. **QUALIFY** - saves a subquery for window filters. Shows you know the engine.
2. **MERGE** - the upsert pattern for incremental loads. Core DE skill.
3. **APPROX_COUNT_DISTINCT** - exact vs approximate tradeoff at scale.
4. **Recursive CTEs** - hierarchy traversal. Know that Spark lacks them.
5. **LATERAL JOIN** - flattening nested data. Know the UNNEST/explode alternatives.

## Choosing Your Dialect for Interviews

- **Company uses BigQuery**: emphasize QUALIFY, MERGE, UNNEST patterns, cost awareness (bytes scanned)
- **Company uses Snowflake**: emphasize QUALIFY, MERGE, VARIANT/FLATTEN, warehouse sizing
- **Company uses Spark/Databricks**: emphasize DataFrame operations, no recursive CTEs, Delta MERGE, broadcast joins
- **Company uses Postgres**: emphasize INSERT ON CONFLICT, jsonb, EXPLAIN ANALYZE, expression indexes
- **Generic/unknown**: use standard SQL and mention dialect variations. DuckDB syntax is a good default since it supports the most features.
