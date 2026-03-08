# Approximate Counting

## Overview

Exact COUNT(DISTINCT) requires storing every unique value in a hash set. For high-cardinality columns (100M+ unique values), this consumes gigabytes of memory. Approximate counting using HyperLogLog (HLL) achieves ~2% accuracy with only 16KB of memory, regardless of cardinality.

The trade-off is simple: exact answers cost O(n) memory, approximate answers cost O(1) memory.

## Exact vs Approximate

### Exact COUNT(DISTINCT)

```sql
SELECT COUNT(DISTINCT user_id) AS exact_count
FROM page_views;
```

Builds a hash set of all distinct values. Memory is O(distinct values). For 100M unique user_ids (8 bytes each), the hash set is roughly 1.5-2GB.

### APPROX_COUNT_DISTINCT

```sql
SELECT APPROX_COUNT_DISTINCT(user_id) AS approx_count
FROM page_views;
```

Uses the HyperLogLog algorithm. Memory is O(1), typically 16KB regardless of input size. Standard error is ~2% (varies by implementation precision).

## Side-by-Side Comparison

```sql
SELECT
    COUNT(DISTINCT user_id) AS exact_count,
    APPROX_COUNT_DISTINCT(user_id) AS approx_count,
    ROUND(
        100.0 * ABS(COUNT(DISTINCT user_id) - APPROX_COUNT_DISTINCT(user_id))
        / COUNT(DISTINCT user_id),
        2
    ) AS error_pct
FROM page_views;
```

Typical output on 1M rows with ~100K distinct users:
```
exact_count | approx_count | error_pct
99847       | 101234       | 1.39
```

## HyperLogLog: How It Works

HLL estimates cardinality by observing the distribution of hash values:

1. Hash each value to a uniform random bit string
2. Count the maximum number of leading zeros across all hashes
3. The maximum leading-zero count estimates log2(cardinality)

With 2^14 (16384) registers, each tracking the max leading-zero count for its hash bucket, HLL achieves ~1.04/sqrt(16384) = ~0.8% standard error. In practice, implementations report ~2% error at the 95th percentile.

HLL sketches are **mergeable**: you can compute HLL per partition, then combine them for the global count. This is why HLL works perfectly in distributed engines where each node computes a local sketch.

## When to Use Each

| Use Case | Exact | Approximate |
|---|---|---|
| Billing (unique users per account) | Yes | No |
| Compliance reporting | Yes | No |
| Dashboard metrics (DAU, unique visitors) | Optional | Yes |
| Pipeline monitoring (cardinality drift) | No | Yes |
| Ad-hoc exploration ("roughly how many?") | No | Yes |
| Real-time streaming counters | No | Yes (HLL is streaming-friendly) |

**Decision framework:** If the number feeds into a financial calculation, contract or regulatory report, use exact. If it feeds into a dashboard, alert threshold or exploratory analysis, approximate is fine.

## Dialect Notes

| Engine | Function | Algorithm | Default Error |
|---|---|---|---|
| DuckDB | APPROX_COUNT_DISTINCT | HLL | ~2% |
| BigQuery | APPROX_COUNT_DISTINCT | HLL++ | ~1% |
| Snowflake | APPROX_COUNT_DISTINCT | HLL | ~2% |
| Spark | approx_count_distinct | HLL | ~5% (configurable) |
| Postgres | No built-in (use HLL extension) | HLL | ~2% |
| Redis | PFADD / PFCOUNT | HLL | ~0.8% |

BigQuery's HLL++ is an improved version of HLL with better accuracy for small cardinalities.

## At Scale

| Scenario | Exact COUNT(DISTINCT) | APPROX_COUNT_DISTINCT |
|---|---|---|
| 1M rows, 100K unique | ~15MB hash set, < 1 sec | 16KB, < 1 sec |
| 100M rows, 10M unique | ~150MB hash set, 5-15 sec | 16KB, 2-5 sec |
| 1B rows, 100M unique | ~2GB hash set, 1-5 min | 16KB, 10-30 sec |
| 10B rows, 1B unique | ~16GB (may spill), 10+ min | 16KB, 1-3 min |

The time savings come from two sources: less memory allocation/management and the ability to use streaming aggregation (no hash table resizing, no spill-to-disk).

In distributed engines, exact COUNT(DISTINCT) requires a global shuffle of all values to one node for deduplication. APPROX_COUNT_DISTINCT shuffles only the HLL sketches (16KB per node), which is orders of magnitude less data.

## Beyond Counting: Other Approximate Aggregations

- **APPROX_QUANTILE / APPROX_PERCENTILE:** Estimate median, p95, p99 without sorting. Uses t-digest or GK algorithm.
- **APPROX_TOP_K:** Find the most frequent values without counting all. Uses Count-Min Sketch or Space-Saving.
- **MinHash:** Estimate set similarity (Jaccard index) between two sets of values.

These share the same design principle: trade a small amount of accuracy for massive memory and speed improvements.

## Connection to Pattern 11 (Probabilistic Data Structures)

APPROX_COUNT_DISTINCT is HyperLogLog applied as a SQL aggregate. See Pattern 11 for the algorithmic details: hash functions, register arrays, harmonic mean estimation and bias correction. The key insight is that HLL reduces a set membership problem to a statistical estimation problem.
