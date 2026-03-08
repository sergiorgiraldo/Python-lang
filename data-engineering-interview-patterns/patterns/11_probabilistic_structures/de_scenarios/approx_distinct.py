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
