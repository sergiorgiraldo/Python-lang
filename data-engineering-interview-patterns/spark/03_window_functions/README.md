# Window Functions

## Pattern Connection

Maps to [`patterns/04_sliding_window/`](../../patterns/04_sliding_window/README.md)
(maintaining state across ordered elements) and
[`sql/01_window_functions/`](../../sql/01_window_functions/README.md)
(ROW_NUMBER, RANK, running totals, sessionization).

In Python you iterate through sorted data maintaining a running state. In SQL you
write `OVER (PARTITION BY ... ORDER BY ...)`. PySpark's Window API is the bridge
between these two: it looks like SQL semantics but executes as a distributed sort
and scan across partitions.

## Key Concepts

**Window specification:** `Window.partitionBy("key").orderBy("ts")`
- `partitionBy` groups rows (like GROUP BY but keeps all rows)
- `orderBy` sorts within each partition
- Frame clause controls which rows are included in each calculation

**Frame types:**
- `rowsBetween(start, end)` - fixed number of rows (positional)
- `rangeBetween(start, end)` - value-based range (e.g., within 7 days)
- `Window.unboundedPreceding` and `Window.currentRow` for running totals

**Ranking functions:** `row_number()`, `rank()`, `dense_rank()`
- `row_number()` - sequential integers, no ties (most common for dedup)
- `rank()` - same rank for ties, gaps after ties (1, 2, 2, 4)
- `dense_rank()` - same rank for ties, no gaps (1, 2, 2, 3)

**Performance:** Window functions require a sort within each partition. If data is
already partitioned by the `partitionBy` key, no shuffle is needed. Otherwise Spark
shuffles first then sorts.

## Interview Context

Window functions are the most common PySpark interview topic after joins. The
classic question is: "Deduplicate this DataFrame keeping the most recent record
per key." Sessionization (assigning events to sessions based on inactivity gaps)
is another frequent topic that combines LAG with cumulative SUM.

## Files

| File | Description |
|---|---|
| `ranking_and_dedup.py` | ROW_NUMBER dedup, RANK vs DENSE_RANK comparison, DataFrame API vs SQL |
| `running_aggregates.py` | Running sum, moving average, rowsBetween vs rangeBetween |
| `sessionization.py` | Session assignment using LAG + cumulative SUM over windows |
