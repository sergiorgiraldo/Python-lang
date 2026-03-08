# DE Scenario: Build Lookup Table for Enrichment

**Run it:** `uv run python -m patterns.01_hash_map.de_scenarios.build_lookup_table`

## Real-World Context

You're processing a stream of events that contain user IDs. Each event needs to be enriched with user metadata (name, email, account tier) from a reference table. The reference table fits in memory.

This comes up constantly: enriching clickstream data with user profiles, adding product details to order events, tagging transactions with merchant categories.

## The Problem

```python
# Reference data (from a dimension table or API)
users = [
    {"id": 1, "name": "Alice", "tier": "premium"},
    {"id": 2, "name": "Bob", "tier": "free"},
    {"id": 3, "name": "Charlie", "tier": "premium"},
]

# Events to enrich
events = [
    {"user_id": 1, "action": "click", "timestamp": "2024-01-15"},
    {"user_id": 2, "action": "view", "timestamp": "2024-01-15"},
    {"user_id": 1, "action": "purchase", "timestamp": "2024-01-16"},
    {"user_id": 999, "action": "click", "timestamp": "2024-01-16"},
]

# Goal: each event gets the user's metadata attached
```

## Worked Example

In data pipelines, enrichment joins are everywhere: you have a stream of events with foreign keys (like a product SKU or user ID) and a dimension table that maps those keys to descriptive attributes. Loading the dimension table into a dict turns each join from an O(n) table scan into an O(1) lookup.

This is the Python equivalent of what a database does when you JOIN on an indexed column. The dict IS the index.

```
Dimension table (10,000 products loaded into a dict at startup):
  lookup = {
    "SKU-1001": {"name": "Wireless Mouse", "category": "Electronics", "price": 29.99},
    "SKU-1002": {"name": "USB Cable", "category": "Electronics", "price": 9.99},
    "SKU-2050": {"name": "Running Shoes", "category": "Apparel", "price": 89.99},
    ... (10,000 entries total)
  }

Event stream (processing one order at a time):
  order_1 = {"order_id": 5001, "sku": "SKU-2050", "qty": 2}
    lookup["SKU-2050"] → found → {"name": "Running Shoes", "category": "Apparel", ...}
    Enriched: {"order_id": 5001, "sku": "SKU-2050", "qty": 2,
               "product_name": "Running Shoes", "category": "Apparel", "unit_price": 89.99}

  order_2 = {"order_id": 5002, "sku": "SKU-1001", "qty": 1}
    lookup["SKU-1001"] → found → {"name": "Wireless Mouse", ...}
    Enriched with product details. One dict lookup.

  order_3 = {"order_id": 5003, "sku": "SKU-9999", "qty": 3}
    lookup["SKU-9999"] → KeyError (product doesn't exist in dimension table)
    Handle gracefully: log the missing SKU, tag the record as unmatched.

Cost: 10 million orders × 1 dict lookup each = 10 million O(1) operations.
Without the dict, each order scans 10,000 products: 10M × 10K = 100 billion comparisons.
That's the difference between seconds and days.
```

## Why Hash Maps

Scanning the reference list for every event is O(n * m) where n is events and m is users. With a million events and a hundred thousand users, that's 100 billion comparisons. A pipeline that should finish in seconds takes hours.

Build a hash map from the reference data once - O(m). Then every lookup is O(1). Total cost drops to O(n + m).

## Production Considerations

**Missing keys are normal.** Events can reference users that don't exist in the reference table (new accounts, data race conditions, bad data). Decide upfront: skip the event, use defaults or route to a dead letter queue.

**Refresh strategy matters.** Reference data changes over time. Options include full refresh on a schedule, CDC-based incremental updates or TTL-based cache expiration.

**Memory limits.** If the reference table doesn't fit in memory, consider an external cache (Redis), a database with indexed lookups or a Bloom filter as a pre-check before hitting the database.

## Connection to LeetCode

This is Two Sum's complement lookup in production form. Build a map once, O(1) lookups for each item. The pattern is identical - only the context changes.

See: [1. Two Sum](../problems/001_two_sum.md)

## Benchmark

See the `.py` file for timing at scale. At 500K events with 50K users, hash map lookup completes in ~0.3s vs a projected ~19s for the naive scan - roughly 70x faster.
