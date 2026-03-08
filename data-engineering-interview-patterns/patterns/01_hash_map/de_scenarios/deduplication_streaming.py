"""
DE Scenario: Deduplication in Streaming Data

Demonstrates three dedup strategies with increasing sophistication:
1. Simple set-based (unbounded memory)
2. Time-windowed (bounded memory)
3. Bloom filter pre-check (probabilistic, very low memory)

Pattern: Hash Map / Set - Existence Check (same as Contains Duplicate)
"""

import random
import time
from collections import OrderedDict


def dedup_simple(events: list[dict], key: str = "event_id") -> list[dict]:
    """
    Simple set-based deduplication.

    Tracks every seen key in a set. O(1) per lookup.
    Memory grows unbounded - fine for batch jobs or small streams.

    Args:
        events: List of event dicts.
        key: Field name to deduplicate on.

    Returns:
        List of unique events (first occurrence kept).
    """
    seen: set[str] = set()
    unique: list[dict] = []

    for event in events:
        event_key = event[key]
        if event_key not in seen:
            seen.add(event_key)
            unique.append(event)

    return unique


def dedup_windowed(
    events: list[dict],
    key: str = "event_id",
    max_window: int = 10_000,
) -> list[dict]:
    """
    Time-windowed deduplication with bounded memory.

    Uses an OrderedDict as an LRU-style window. When the window
    exceeds max_window, the oldest entries are evicted. This means
    very old duplicates might slip through, but recent ones are caught.

    In production, the window is usually time-based (e.g., 1 hour).
    Here we use a count-based window for simplicity.

    Args:
        events: List of event dicts.
        key: Field name to deduplicate on.
        max_window: Maximum number of keys to remember.

    Returns:
        List of unique events within the window.
    """
    seen: OrderedDict[str, None] = OrderedDict()
    unique: list[dict] = []

    for event in events:
        event_key = event[key]
        if event_key not in seen:
            unique.append(event)

        # Move to end (most recent) whether new or duplicate
        seen[event_key] = None
        seen.move_to_end(event_key)

        # Evict oldest if window is full
        while len(seen) > max_window:
            seen.popitem(last=False)

    return unique


class BloomFilter:
    """
    Minimal Bloom filter for dedup pre-checking.

    Uses Python's built-in hash with multiple seeds. In production,
    you'd use mmh3 or xxhash for better distribution.

    False positive rate depends on size and number of hash functions.
    False negatives are impossible - if the filter says "not seen,"
    it's definitely not seen.
    """

    def __init__(self, size: int = 1_000_000, num_hashes: int = 5) -> None:
        self.size = size
        self.num_hashes = num_hashes
        self.bit_array = bytearray(size)

    def add(self, item: str) -> None:
        for seed in range(self.num_hashes):
            idx = hash((item, seed)) % self.size
            self.bit_array[idx] = 1

    def might_contain(self, item: str) -> bool:
        return all(
            self.bit_array[hash((item, seed)) % self.size]
            for seed in range(self.num_hashes)
        )


def dedup_bloom(
    events: list[dict],
    key: str = "event_id",
    bloom_size: int = 1_000_000,
) -> list[dict]:
    """
    Bloom filter deduplication.

    Fast pre-check with very low memory. May have false positives
    (dropping a unique event it thinks is a duplicate) but never
    false negatives (letting a duplicate through).

    In production, Bloom filter positives are typically verified
    against an authoritative store. Here we accept the small
    false positive rate for simplicity.

    Args:
        events: List of event dicts.
        key: Field name to deduplicate on.
        bloom_size: Size of the Bloom filter bit array.

    Returns:
        List of likely-unique events.
    """
    bf = BloomFilter(size=bloom_size)
    unique: list[dict] = []

    for event in events:
        event_key = event[key]
        if not bf.might_contain(event_key):
            unique.append(event)
            bf.add(event_key)

    return unique


if __name__ == "__main__":
    # Correctness check
    events = [
        {"event_id": "e001", "user": "alice", "action": "purchase"},
        {"event_id": "e002", "user": "bob", "action": "click"},
        {"event_id": "e001", "user": "alice", "action": "purchase"},
        {"event_id": "e003", "user": "charlie", "action": "view"},
        {"event_id": "e002", "user": "bob", "action": "click"},
    ]

    simple = dedup_simple(events)
    assert len(simple) == 3
    assert [e["event_id"] for e in simple] == ["e001", "e002", "e003"]
    print(f"Simple dedup: {len(events)} events -> {len(simple)} unique")

    windowed = dedup_windowed(events, max_window=2)
    print(f"Windowed dedup (window=2): {len(events)} events -> {len(windowed)} unique")

    bloom = dedup_bloom(events)
    assert len(bloom) == 3
    print(f"Bloom dedup: {len(events)} events -> {len(bloom)} unique")

    # Benchmark at scale
    print("\n--- Benchmark ---")
    num_events = 1_000_000
    dup_rate = 0.2  # 20% duplicates

    random.seed(42)
    unique_count = int(num_events * (1 - dup_rate))
    event_ids = [f"evt-{i}" for i in range(unique_count)]
    # Add duplicates by repeating some IDs
    all_ids = event_ids + random.choices(event_ids, k=num_events - unique_count)
    random.shuffle(all_ids)
    large_events = [{"event_id": eid, "data": "x"} for eid in all_ids]

    for name, func in [
        ("Simple set", dedup_simple),
        ("Windowed (10K)", lambda e: dedup_windowed(e, max_window=10_000)),
        ("Bloom filter", dedup_bloom),
    ]:
        start = time.perf_counter()
        result = func(large_events)
        elapsed = time.perf_counter() - start
        print(f"{name}: {elapsed:.3f}s -> {len(result):,} unique from {num_events:,}")
