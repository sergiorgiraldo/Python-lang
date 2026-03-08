# CC Prompt: Create Pattern 11 Probabilistic Structures (Part 5 of 5)

## What This Prompt Does

Creates all 4 DE scenarios: Stream Deduplication (Bloom), Approximate Distinct Count (HLL), Heavy Hitter Detection (CMS), and Memory Budget Analysis (comparison).

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Every .md Worked Example starts with a prose paragraph
- DE scenarios include both .py (runnable with demo) and .md (documented)

---

## DE Scenario 1: Stream Deduplication

### `de_scenarios/stream_dedup.py`

```python
"""
DE Scenario: Stream deduplication using Bloom filters.

Real-world application: event pipelines receive duplicate events
(retries, at-least-once delivery). Checking a database for every event
is expensive. A Bloom filter pre-filters: if the filter says "new,"
the event is definitely new. If it says "seen," do the DB check
(might be a false positive).

Run: uv run python -m patterns.11_probabilistic_structures.de_scenarios.stream_dedup
"""

import sys
import time
sys.path.insert(0, "patterns/11_probabilistic_structures/problems")

from bloom_filter import BloomFilter


def simulate_stream_dedup(
    events: list[str],
    expected_unique: int,
    fp_rate: float = 0.01,
) -> dict:
    """
    Simulate stream deduplication with a Bloom filter pre-filter.

    Returns stats on how many DB lookups were saved.
    """
    bf = BloomFilter(expected_unique, fp_rate)
    seen_exact: set[str] = set()  # simulates the database

    stats = {
        "total_events": 0,
        "true_new": 0,
        "true_duplicate": 0,
        "bloom_said_new": 0,
        "bloom_said_seen": 0,
        "false_positives": 0,  # bloom said seen, but was actually new
        "db_lookups_saved": 0,
    }

    for event_id in events:
        stats["total_events"] += 1
        is_actually_new = event_id not in seen_exact

        if bf.might_contain(event_id):
            # Bloom says "maybe seen" - need to check DB
            stats["bloom_said_seen"] += 1
            if is_actually_new:
                stats["false_positives"] += 1
                # False positive: bloom was wrong, item is actually new
                seen_exact.add(event_id)
                bf.add(event_id)
                stats["true_new"] += 1
            else:
                stats["true_duplicate"] += 1
        else:
            # Bloom says "definitely new" - no DB check needed
            stats["bloom_said_new"] += 1
            stats["db_lookups_saved"] += 1
            seen_exact.add(event_id)
            bf.add(event_id)
            stats["true_new"] += 1

    stats["bloom_memory_bytes"] = bf.memory_bytes
    stats["exact_set_estimate_bytes"] = len(seen_exact) * 70  # rough estimate

    return stats


if __name__ == "__main__":
    import random

    print("=== Stream Deduplication with Bloom Filter ===\n")

    # Generate events: 100K unique, 30% duplicates
    unique_events = [f"evt_{i:06d}" for i in range(100000)]
    duplicates = random.choices(unique_events, k=30000)
    all_events = unique_events + duplicates
    random.shuffle(all_events)

    stats = simulate_stream_dedup(all_events, expected_unique=100000)

    print(f"  Total events:       {stats['total_events']:,}")
    print(f"  True new:           {stats['true_new']:,}")
    print(f"  True duplicates:    {stats['true_duplicate']:,}")
    print(f"  False positives:    {stats['false_positives']:,}")
    print(f"  DB lookups saved:   {stats['db_lookups_saved']:,} "
          f"({stats['db_lookups_saved']/stats['total_events']:.1%})")
    print(f"  Bloom memory:       {stats['bloom_memory_bytes']:,} bytes")
    print(f"  Exact set estimate: {stats['exact_set_estimate_bytes']:,} bytes")
    print(f"  Memory savings:     "
          f"{stats['exact_set_estimate_bytes']/stats['bloom_memory_bytes']:.0f}x")
```

### `de_scenarios/stream_dedup.md`

````markdown
# DE Scenario: Stream Deduplication

## Real-World Context

Event pipelines using Kafka, Kinesis or Pub/Sub typically provide at-least-once delivery. Duplicate events arrive from retries, reprocessing and consumer restarts. Deduplicating requires checking "have I seen this event ID before?" for every event.

Checking a database for each event at 100K events/second means 100K DB queries/second. A Bloom filter pre-filter eliminates the DB lookup for events that are definitely new (the common case), reducing DB load by 90%+.

## Worked Example

The Bloom filter sits in front of the database as a fast, in-memory pre-filter. Events that the filter says are "definitely new" skip the DB entirely. Events that the filter says are "possibly seen" still need a DB check (some will be false positives).

```
Stream: [evt_001, evt_002, evt_001, evt_003, evt_002, evt_004, ...]

Event evt_001 (first time):
  Bloom check: all bits at 0 → DEFINITELY NEW
  Skip DB lookup (saved). Add to Bloom + DB.

Event evt_002 (first time):
  Bloom check: → DEFINITELY NEW
  Skip DB lookup (saved). Add to Bloom + DB.

Event evt_001 (duplicate):
  Bloom check: all bits set → POSSIBLY SEEN
  DB lookup: yes, exists → TRUE DUPLICATE. Drop.

Event evt_005 (first time, false positive):
  Bloom check: all bits set (collision) → POSSIBLY SEEN
  DB lookup: not found → FALSE POSITIVE. Add to Bloom + DB.

Results for 130K events (100K unique + 30K duplicates):
  DB lookups saved: ~99K (for definitely-new events)
  False positives: ~1K (checked DB unnecessarily)
  Memory: ~120 KB (Bloom) vs ~7 MB (exact set)
```
````

---

## DE Scenario 2: Approximate Distinct Count

### `de_scenarios/approx_distinct.py`

```python
"""
DE Scenario: Approximate COUNT DISTINCT using HyperLogLog.

Real-world application: counting unique users, unique sessions,
unique queries across billions of events. Exact counting requires
storing all unique values. HLL does it in 16 KB.

Run: uv run python -m patterns.11_probabilistic_structures.de_scenarios.approx_distinct
"""

import sys
import time
sys.path.insert(0, "patterns/11_probabilistic_structures/problems")

from hyperloglog import HyperLogLog


def compare_exact_vs_hll(
    items: list[str], precision: int = 14
) -> dict:
    """
    Compare exact COUNT DISTINCT vs HLL estimate.
    """
    # Exact counting
    start = time.time()
    exact_set: set[str] = set()
    for item in items:
        exact_set.add(item)
    exact_time = time.time() - start
    exact_count = len(exact_set)

    # HLL estimation
    start = time.time()
    hll = HyperLogLog(precision=precision)
    for item in items:
        hll.add(item)
    hll_time = time.time() - start
    hll_estimate = hll.estimate()

    error = abs(hll_estimate - exact_count) / exact_count if exact_count > 0 else 0

    return {
        "total_items": len(items),
        "exact_count": exact_count,
        "hll_estimate": hll_estimate,
        "error_percent": error * 100,
        "exact_memory_bytes": sys.getsizeof(exact_set) + sum(
            sys.getsizeof(s) for s in list(exact_set)[:100]
        ) // 100 * len(exact_set),
        "hll_memory_bytes": hll.memory_bytes,
        "exact_time_ms": exact_time * 1000,
        "hll_time_ms": hll_time * 1000,
    }


def demonstrate_merge():
    """Show distributed counting with HLL merge."""
    # Simulate 3 workers processing different shards
    worker_hlls: list[HyperLogLog] = []

    for shard in range(3):
        hll = HyperLogLog(precision=14)
        for i in range(50000):
            # Some overlap between shards
            user_id = f"user_{i + shard * 30000}"
            hll.add(user_id)
        worker_hlls.append(hll)
        print(f"    Worker {shard}: {hll.estimate():,} estimated unique users")

    # Merge all workers
    merged = worker_hlls[0]
    for other in worker_hlls[1:]:
        merged = merged.merge(other)

    return merged.estimate()


if __name__ == "__main__":
    print("=== Approximate COUNT DISTINCT ===\n")

    # Simulate event stream with many duplicates
    import random

    unique_users = [f"user_{i:08d}" for i in range(500000)]
    # Each user generates 5-20 events
    events = []
    for user in unique_users:
        events.extend([user] * random.randint(5, 20))
    random.shuffle(events)

    print(f"  Events: {len(events):,}")
    result = compare_exact_vs_hll(events)

    print(f"  Exact distinct: {result['exact_count']:,}")
    print(f"  HLL estimate:   {result['hll_estimate']:,}")
    print(f"  Error:          {result['error_percent']:.2f}%")
    print(f"  HLL memory:     {result['hll_memory_bytes']:,} bytes ({result['hll_memory_bytes']/1024:.0f} KB)")
    print(f"  Exact time:     {result['exact_time_ms']:.0f} ms")
    print(f"  HLL time:       {result['hll_time_ms']:.0f} ms")

    print(f"\n  === Distributed Counting (3 workers) ===")
    merged_estimate = demonstrate_merge()
    print(f"    Merged estimate: {merged_estimate:,}")
```

### `de_scenarios/approx_distinct.md`

````markdown
# DE Scenario: Approximate Distinct Count

## Real-World Context

"How many unique users visited yesterday?" sounds simple. With 500M events and 50M unique users, an exact COUNT DISTINCT requires a hash set holding 50M entries (~3.5 GB of RAM) or a database sort/hash operation. BigQuery and Snowflake offer APPROX_COUNT_DISTINCT() which uses HyperLogLog internally to answer this in 16 KB with ~1% error.

Understanding HLL helps you:
- Explain the ~1% discrepancy when stakeholders compare exact vs approximate counts
- Choose precision settings based on accuracy requirements
- Use merge operations for distributed counting across shards or time windows

## Worked Example

HLL provides fixed-memory cardinality estimation regardless of dataset size. The merge operation (element-wise max of registers) enables distributed counting: each worker processes its shard independently, then the coordinator merges all HLLs for the global estimate.

```
Scenario: 5M events from 500K unique users

Exact approach:
  HashSet of user IDs → 500K entries → ~35 MB memory
  Time: ~800 ms (hashing + set operations)

HLL approach (p=14):
  16,384 registers → 16 KB memory (2,100x smaller)
  Time: ~600 ms
  Estimate: 498,200 (error: 0.36%)

Distributed counting (3 Kafka partitions):
  Worker 0: processes events for users 0-200K → HLL estimate: 201K
  Worker 1: processes events for users 150K-350K → HLL estimate: 199K
  Worker 2: processes events for users 300K-500K → HLL estimate: 198K

  Merge: max(register[i]) across all 3 workers
  Merged estimate: 497,800 (error: 0.44%)
  Note: overlapping users are handled automatically by the max operation

SQL equivalent:
  SELECT APPROX_COUNT_DISTINCT(user_id) FROM events
  WHERE event_date = '2024-01-15';
  -- Returns: 498,200 (same result, ~16 KB internal state)
```
````

---

## DE Scenario 3: Heavy Hitter Detection

### `de_scenarios/heavy_hitters.py`

```python
"""
DE Scenario: Heavy hitter (hot key) detection using Count-Min Sketch.

Real-world application: identifying hot partition keys that cause skew
in distributed systems. If one key gets 10% of all traffic, any
hash-partitioned system will bottleneck on that partition.

Run: uv run python -m patterns.11_probabilistic_structures.de_scenarios.heavy_hitters
"""

import sys
import random
sys.path.insert(0, "patterns/11_probabilistic_structures/problems")

from count_min_sketch import CountMinSketchWithHeavyHitters


def simulate_hot_key_detection(
    events: list[str],
    threshold: float = 0.01,
) -> dict:
    """Detect hot keys in a stream of partition keys."""
    hh = CountMinSketchWithHeavyHitters(width=2000, depth=5, top_k=50)

    for event in events:
        hh.add(event)

    detected = hh.heavy_hitters(threshold)

    return {
        "total_events": len(events),
        "threshold": threshold,
        "detected_hot_keys": [(k, v) for k, v in sorted(detected, key=lambda x: -x[1])],
        "memory_bytes": hh.cms.memory_bytes,
    }


if __name__ == "__main__":
    print("=== Heavy Hitter Detection ===\n")

    # Simulate key distribution with skew
    # 5 hot keys get 40% of traffic, 10K normal keys share 60%
    events = []
    hot_keys = [f"hot_key_{i}" for i in range(5)]
    normal_keys = [f"key_{i:05d}" for i in range(10000)]

    # Hot keys: 8% each (40% total)
    for key in hot_keys:
        events.extend([key] * 8000)

    # Normal keys: ~6 each (60% total)
    for key in normal_keys:
        events.extend([key] * random.randint(4, 8))

    random.shuffle(events)

    print(f"  Total events: {len(events):,}")
    print(f"  Hot keys: {len(hot_keys)}")
    print(f"  Normal keys: {len(normal_keys):,}")

    result = simulate_hot_key_detection(events, threshold=0.01)

    print(f"\n  Detected hot keys (>{result['threshold']:.0%} of traffic):")
    for key, count in result["detected_hot_keys"][:10]:
        pct = count / result["total_events"] * 100
        print(f"    {key}: ~{count:,} events ({pct:.1f}%)")

    print(f"\n  CMS memory: {result['memory_bytes']:,} bytes")
    print(f"  Exact tracking would need: ~{len(set(events)) * 70:,} bytes")
```

### `de_scenarios/heavy_hitters.md`

````markdown
# DE Scenario: Heavy Hitter Detection

## Real-World Context

In distributed data systems, "hot keys" cause skew. If a Kafka topic is partitioned by customer_id and one customer generates 10% of all events, that partition's consumer falls behind while others idle. Detecting hot keys in real time helps trigger alerts, repartitioning or special handling.

A Count-Min Sketch tracks approximate frequencies for all keys using fixed memory, paired with a small heap to track the top candidates.

## Worked Example

The CMS estimates frequencies for every key seen in the stream. A threshold (e.g., 1% of total traffic) identifies which keys are "hot." The CMS never under-counts, so any key above the threshold is flagged. Some keys slightly below the threshold might be flagged too (over-counting), but hot keys are never missed.

```
Stream: 100K events across 10,005 unique keys
  5 hot keys: ~8,000 events each (8% of traffic)
  10,000 normal keys: ~6 events each

CMS tracking (width=2000, depth=5):
  After processing all events:

  estimate("hot_key_0") = 8,012   (true: 8,000, over-count: 12)
  estimate("hot_key_1") = 8,003   (true: 8,000, over-count: 3)
  estimate("key_00042") = 9       (true: 6, over-count: 3)

  Threshold: 1% of 100K = 1,000 events

  Heavy hitters detected:
    hot_key_0: ~8,012 (8.0%)  ← correctly flagged
    hot_key_1: ~8,003 (8.0%)  ← correctly flagged
    hot_key_2: ~7,998 (8.0%)  ← correctly flagged
    hot_key_3: ~8,015 (8.0%)  ← correctly flagged
    hot_key_4: ~7,991 (8.0%)  ← correctly flagged

  No false positives (normal keys are ~6 events, far below 1K threshold)
  Memory: 80 KB (vs ~700 KB for exact counter per key)
```
````

---

## DE Scenario 4: Memory Budget Analysis

### `de_scenarios/memory_budget.py`

```python
"""
DE Scenario: Compare memory usage of exact vs approximate approaches.

Real-world application: choosing between exact and approximate data
structures based on cardinality, accuracy requirements and memory budget.

Run: uv run python -m patterns.11_probabilistic_structures.de_scenarios.memory_budget
"""

import math
import sys
sys.path.insert(0, "patterns/11_probabilistic_structures/problems")


def estimate_exact_memory(n_items: int, avg_item_bytes: int = 40) -> int:
    """Estimate memory for a Python set of strings."""
    # Python set overhead: ~200 bytes base + 8 bytes per bucket
    # Each string: ~50 bytes overhead + string content
    set_overhead = 200 + n_items * 8
    item_memory = n_items * (50 + avg_item_bytes)
    return set_overhead + item_memory


def estimate_bloom_memory(n_items: int, fp_rate: float = 0.01) -> int:
    """Estimate Bloom filter memory."""
    m = int(math.ceil(-(n_items * math.log(fp_rate)) / (math.log(2) ** 2)))
    return math.ceil(m / 8)


def estimate_hll_memory(precision: int = 14) -> int:
    """HLL memory is fixed regardless of cardinality."""
    return 1 << precision


def estimate_cms_memory(width: int = 2000, depth: int = 5) -> int:
    """CMS memory is fixed."""
    return width * depth * 8  # 8 bytes per counter


def comparison_table(cardinalities: list[int]) -> list[dict]:
    """Build comparison table across cardinalities."""
    results = []

    for n in cardinalities:
        results.append({
            "cardinality": n,
            "exact_set_bytes": estimate_exact_memory(n),
            "bloom_1pct_bytes": estimate_bloom_memory(n, 0.01),
            "bloom_01pct_bytes": estimate_bloom_memory(n, 0.001),
            "hll_bytes": estimate_hll_memory(14),
            "cms_bytes": estimate_cms_memory(2000, 5),
        })

    return results


def format_bytes(b: int) -> str:
    """Format bytes as human-readable."""
    if b < 1024:
        return f"{b} B"
    elif b < 1024 ** 2:
        return f"{b / 1024:.1f} KB"
    elif b < 1024 ** 3:
        return f"{b / 1024**2:.1f} MB"
    else:
        return f"{b / 1024**3:.1f} GB"


if __name__ == "__main__":
    print("=== Memory Budget Analysis ===\n")
    print("  Comparing exact vs approximate data structure memory usage\n")

    cardinalities = [1_000, 10_000, 100_000, 1_000_000, 10_000_000, 100_000_000]

    results = comparison_table(cardinalities)

    header = f"  {'Cardinality':>15s}  {'Exact Set':>10s}  {'Bloom 1%':>10s}  {'Bloom 0.1%':>10s}  {'HLL':>10s}  {'CMS':>10s}"
    print(header)
    print("  " + "-" * (len(header) - 2))

    for r in results:
        print(
            f"  {r['cardinality']:>15,}  "
            f"{format_bytes(r['exact_set_bytes']):>10s}  "
            f"{format_bytes(r['bloom_1pct_bytes']):>10s}  "
            f"{format_bytes(r['bloom_01pct_bytes']):>10s}  "
            f"{format_bytes(r['hll_bytes']):>10s}  "
            f"{format_bytes(r['cms_bytes']):>10s}"
        )

    print(f"\n  Key takeaway:")
    print(f"    At 100M items:")
    r = results[-1]
    print(f"      Exact set:   {format_bytes(r['exact_set_bytes'])}")
    print(f"      Bloom (1%):  {format_bytes(r['bloom_1pct_bytes'])} "
          f"({r['exact_set_bytes'] / r['bloom_1pct_bytes']:.0f}x smaller)")
    print(f"      HLL:         {format_bytes(r['hll_bytes'])} "
          f"({r['exact_set_bytes'] / r['hll_bytes']:.0f}x smaller)")
```

### `de_scenarios/memory_budget.md`

````markdown
# DE Scenario: Memory Budget Analysis

## Real-World Context

Choosing between exact and approximate data structures is a principal-level decision. The answer depends on cardinality (how many items), accuracy requirements (is 1% error acceptable) and memory budget (what fits in a single machine's RAM).

This analysis shows how the gap between exact and approximate grows with cardinality. At 1K items, exact is fine. At 100M items, exact needs 8+ GB while approximate structures need kilobytes.

## Worked Example

The memory comparison reveals why approximate structures exist. Below 100K items, exact structures fit comfortably in memory and the accuracy trade-off isn't worth it. Above 1M items, the memory savings become significant. Above 100M, approximate structures are often the only option that fits in memory.

```
Cardinality    Exact Set     Bloom 1%   Bloom 0.1%      HLL        CMS
-----------   ----------    ---------   ----------   --------   --------
      1,000      88.0 KB      1.2 KB      1.8 KB    16.0 KB    78.1 KB
     10,000     878.9 KB     11.7 KB     17.6 KB    16.0 KB    78.1 KB
    100,000       8.6 MB    117.2 KB    175.8 KB    16.0 KB    78.1 KB
  1,000,000      85.8 MB      1.1 MB      1.7 MB    16.0 KB    78.1 KB
 10,000,000     858.3 MB     11.4 MB     17.1 MB    16.0 KB    78.1 KB
100,000,000       8.4 GB    114.2 MB    171.4 MB    16.0 KB    78.1 KB

Key observations:
  - Exact set: grows linearly with cardinality. O(n).
  - Bloom filter: grows linearly but ~70x smaller than exact. O(n).
  - HLL: FIXED at 16 KB regardless of cardinality. O(1).
  - CMS: FIXED at ~80 KB regardless of cardinality. O(1).

Decision framework:
  - Need exact membership? Use a set (if it fits) or database.
  - Need approximate membership? Bloom filter.
  - Need approximate count distinct? HLL. Always fits. ~1% error.
  - Need approximate frequency? CMS. Fixed memory.
  - Cardinality under 100K? Just use exact. Memory is cheap.
  - Cardinality over 10M? Approximate is probably necessary.
```
````

---

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== DE Scenario files ==="
ls patterns/11_probabilistic_structures/de_scenarios/*.py patterns/11_probabilistic_structures/de_scenarios/*.md 2>/dev/null

echo ""
echo "=== Run DE scenarios ==="
uv run python -m patterns.11_probabilistic_structures.de_scenarios.stream_dedup 2>&1 | tail -8
echo ""
uv run python -m patterns.11_probabilistic_structures.de_scenarios.approx_distinct 2>&1 | tail -8
echo ""
uv run python -m patterns.11_probabilistic_structures.de_scenarios.heavy_hitters 2>&1 | tail -8
echo ""
uv run python -m patterns.11_probabilistic_structures.de_scenarios.memory_budget 2>&1 | tail -10

echo ""
echo "=== Full Pattern 11 test suite ==="
uv run pytest patterns/11_probabilistic_structures/ -v --tb=short 2>&1 | tail -25

echo ""
echo "=== Pattern 11 completeness ==="
echo "Implementations:"
ls patterns/11_probabilistic_structures/problems/*.md 2>/dev/null | wc -l
echo "(should be 3)"
echo "DE Scenarios:"
ls patterns/11_probabilistic_structures/de_scenarios/*.md 2>/dev/null | wc -l
echo "(should be 4)"
echo "Worked Examples:"
grep -rl "## Worked Example" patterns/11_probabilistic_structures/ | wc -l
echo "(should be 7: 3 implementations + 4 DE scenarios)"

echo ""
echo "=== Style check ==="
grep -r "—" patterns/11_probabilistic_structures/ && echo "❌ Em dashes found" || echo "✅ No em dashes"

echo ""
echo "=== Cross-pattern test suite ==="
uv run pytest --tb=short 2>&1 | tail -3
```
