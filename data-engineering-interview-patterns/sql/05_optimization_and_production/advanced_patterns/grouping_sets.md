# GROUPING SETS, ROLLUP and CUBE

Multi-level aggregation in a single pass over the data.

## When to Use

- Multi-level reporting: daily totals, monthly subtotals, yearly grand totals
- Dimension rollups: product + region breakdowns with subtotals at each level
- Data cubes: all combinations of dimensions for OLAP-style analysis
- Replacing multiple GROUP BY queries UNION ALL'd together

## How It Works

### GROUPING SETS

Explicitly define which grouping combinations you want:

```sql
SELECT region, product, SUM(revenue) AS total
FROM sales
GROUP BY GROUPING SETS (
    (region, product),   -- per region + product
    (region),            -- per region subtotal
    ()                   -- grand total
);
```

Produces rows at three levels. NULL in a column means "all values" for that
dimension (a subtotal/total row).

### ROLLUP

Hierarchical subtotals. `ROLLUP(a, b)` is shorthand for
`GROUPING SETS ((a, b), (a), ())`.

```sql
SELECT region, product, SUM(revenue) AS total
FROM sales
GROUP BY ROLLUP (region, product);
```

Column order matters: ROLLUP removes columns right to left. `ROLLUP(a, b, c)`
produces `(a, b, c), (a, b), (a), ()`.

### CUBE

All possible combinations. `CUBE(a, b)` is shorthand for
`GROUPING SETS ((a, b), (a), (b), ())`.

```sql
SELECT region, product, SUM(revenue) AS total
FROM sales
GROUP BY CUBE (region, product);
```

CUBE produces 2^n grouping sets for n columns. Use with caution on many columns.

## The GROUPING() Function

NULL in a result column is ambiguous: is it a subtotal row, or does the source
data contain NULL? The GROUPING() function resolves this.

```sql
SELECT
    region,
    product,
    SUM(revenue) AS total,
    GROUPING(region) AS is_region_rolled,    -- 1 if region is a subtotal
    GROUPING(product) AS is_product_rolled   -- 1 if product is a subtotal
FROM sales
GROUP BY GROUPING SETS ((region, product), (region), ());
```

- `GROUPING(col) = 0`: the column is part of this grouping level (real value)
- `GROUPING(col) = 1`: the column is aggregated away (subtotal/total row)

## At Scale

One pass over the data instead of N separate GROUP BY + UNION ALL queries.
For a table with billions of rows, this means:
- One scan instead of N scans
- One sort/hash instead of N
- Significantly less I/O and compute

In BigQuery, this directly reduces bytes scanned (one scan vs N).
In Snowflake, this reduces warehouse compute time.

## Dialect Notes

Syntax is identical across all major engines: DuckDB, BigQuery, Snowflake,
Spark SQL and Postgres all support GROUPING SETS, ROLLUP, CUBE and the
GROUPING() function with the same syntax.

## Row Count Guide

Given the sales table with 2 regions and 2 products:
- **GROUPING SETS ((region, product), (region), ())**: 2*2 + 2 + 1 = **7 rows**
- **ROLLUP (region, product)**: same as above = **7 rows**
- **CUBE (region, product)**: 2*2 + 2 + 2 + 1 = **9 rows** (adds per-product totals)
