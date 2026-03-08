# DE Scenario: Single-Pass Aggregation (GROUP BY in Python)

**Run it:** `uv run python -m patterns.01_hash_map.de_scenarios.single_pass_aggregation`

## Real-World Context

You need to compute aggregations (counts, sums, averages) grouped by a key. In SQL this is a `GROUP BY`. In Python - when processing files, API responses or streaming data - you implement it with a hash map.

This comes up when SQL isn't available: processing JSON from an API, transforming data in a Lambda function, building custom aggregations in a streaming pipeline.

## The Problem

```python
transactions = [
    {"category": "food", "amount": 12.50},
    {"category": "transport", "amount": 35.00},
    {"category": "food", "amount": 8.75},
    {"category": "entertainment", "amount": 15.00},
    {"category": "food", "amount": 22.00},
    {"category": "transport", "amount": 12.00},
]

# Goal: total and count per category, in one pass
```

## Worked Example

GROUP BY in SQL aggregates rows by key in a single pass through the data. The Python equivalent uses a dict: the key is the grouping column (department, region, date) and the value accumulates the aggregation state (count, sum, min, max). One pass through the data, one dict lookup per record. This is what Spark and Pandas do under the hood for `groupby().agg()`.

We use a `defaultdict` here so that accessing a missing key automatically creates a new aggregation bucket rather than crashing with a KeyError.

```
Input records (employee data, arriving one at a time):
  {"dept": "engineering",  "salary": 95000,  "level": "senior"}
  {"dept": "sales",        "salary": 62000,  "level": "mid"}
  {"dept": "engineering",  "salary": 110000, "level": "staff"}
  {"dept": "marketing",    "salary": 58000,  "level": "mid"}
  {"dept": "sales",        "salary": 72000,  "level": "senior"}
  {"dept": "engineering",  "salary": 88000,  "level": "mid"}
  {"dept": "marketing",    "salary": 65000,  "level": "senior"}

Single-pass aggregation (dict key = dept, value = running totals):
  rec 1: agg["engineering"] = {"count": 1, "total": 95000, "min": 95000, "max": 95000}
  rec 2: agg["sales"]       = {"count": 1, "total": 62000, "min": 62000, "max": 62000}
  rec 3: agg["engineering"] = {"count": 2, "total": 205000, "min": 95000, "max": 110000}
  rec 4: agg["marketing"]   = {"count": 1, "total": 58000, "min": 58000, "max": 58000}
  rec 5: agg["sales"]       = {"count": 2, "total": 134000, "min": 62000, "max": 72000}
  rec 6: agg["engineering"] = {"count": 3, "total": 293000, "min": 88000, "max": 110000}
  rec 7: agg["marketing"]   = {"count": 2, "total": 123000, "min": 58000, "max": 65000}

Final results:
  engineering:  count=3, avg=97,667, range=[88K, 110K]
  sales:        count=2, avg=67,000, range=[62K, 72K]
  marketing:    count=2, avg=61,500, range=[58K, 65K]

7 records, 7 dict lookups, 7 updates. One pass through the data.

Equivalent SQL:
  SELECT dept, COUNT(*), AVG(salary), MIN(salary), MAX(salary)
  FROM employees
  GROUP BY dept

The dict-based approach does the same thing. Each unique dept value
becomes a key, and the aggregation state accumulates as records arrive.
```

## Why Hash Maps

Multiple passes over the data means multiple reads. For files on disk, that's I/O cost. For streaming data, you might not be able to re-read at all. For large datasets, the difference between one pass and two passes is real.

This is the frequency counting hash map pattern. Instead of counting occurrences, you accumulate arbitrary aggregations. `defaultdict` or `Counter` handles the grouping. One pass through the data, O(n) total.

## Production Considerations

**Memory scales with cardinality, not volume.** A billion transactions across 10 categories only needs memory for 10 groups. A million transactions across 500K unique users needs memory for 500K groups. Know your cardinality.

**Partial aggregations enable parallelism.** If you split data across workers, each computes local aggregates. Merge the partial results at the end. This is exactly how MapReduce and Spark work.

## Connection to LeetCode

This is Group Anagrams (LeetCode 49) and Top K Frequent Elements (LeetCode 347) in production form. Group by key, accumulate per group, optionally rank the results.

See: [49. Group Anagrams](../problems/049_group_anagrams.md), [347. Top K Frequent Elements](../problems/347_top_k_frequent.md)

## Benchmark

See the `.py` file for timing at scale. Multi-metric aggregation over 1M records with 100 groups completes in ~0.2s - a single pass.
