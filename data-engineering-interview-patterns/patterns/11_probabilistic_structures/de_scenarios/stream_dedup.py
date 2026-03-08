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
