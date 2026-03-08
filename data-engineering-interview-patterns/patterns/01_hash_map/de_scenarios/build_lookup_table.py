"""
DE Scenario: Build Lookup Table for Enrichment

Demonstrates the performance difference between nested-loop
lookups (O(n*m)) and hash map lookups (O(n+m)) when enriching
events with reference data.

Pattern: Hash Map - Complement Lookup (same as Two Sum)
"""

import time


def enrich_naive(events: list[dict], users: list[dict]) -> list[dict]:
    """
    Naive approach: scan the user list for every event.

    Time: O(n * m) where n = events, m = users
    """
    enriched = []
    for event in events:
        user_data = None
        for user in users:
            if user["id"] == event["user_id"]:
                user_data = user
                break
        enriched.append({**event, "user": user_data})
    return enriched


def enrich_with_lookup(events: list[dict], users: list[dict]) -> list[dict]:
    """
    Optimal approach: build a lookup table, then O(1) per event.

    Time: O(n + m)
    Space: O(m) for the lookup table
    """
    user_lookup = {user["id"]: user for user in users}

    enriched = []
    for event in events:
        user_data = user_lookup.get(event["user_id"])
        enriched.append({**event, "user": user_data})
    return enriched


def enrich_with_default(
    events: list[dict],
    users: list[dict],
    default_user: dict | None = None,
) -> list[dict]:
    """
    Production variant: use a default for missing users instead of None.

    This is common when downstream systems can't handle nulls or when
    you want to flag unmatched events for investigation.
    """
    if default_user is None:
        default_user = {"id": -1, "name": "UNKNOWN", "tier": "unknown"}

    user_lookup = {user["id"]: user for user in users}

    enriched = []
    for event in events:
        user_data = user_lookup.get(event["user_id"], default_user)
        enriched.append({**event, "user": user_data})
    return enriched


if __name__ == "__main__":
    # Small-scale correctness check
    users = [
        {"id": 1, "name": "Alice", "tier": "premium"},
        {"id": 2, "name": "Bob", "tier": "free"},
        {"id": 3, "name": "Charlie", "tier": "premium"},
    ]
    events = [
        {"user_id": 1, "action": "click"},
        {"user_id": 999, "action": "view"},  # unknown user
    ]

    result = enrich_with_lookup(events, users)
    assert result[0]["user"]["name"] == "Alice"
    assert result[1]["user"] is None
    print("Correctness check passed.")

    result_default = enrich_with_default(events, users)
    assert result_default[1]["user"]["name"] == "UNKNOWN"
    print("Default handling check passed.")

    # Benchmark at scale
    print("\n--- Benchmark ---")
    num_users = 50_000
    num_events = 500_000

    users_large = [
        {"id": i, "name": f"User{i}", "tier": "free"} for i in range(num_users)
    ]
    events_large = [
        {"user_id": i % num_users, "action": "click"} for i in range(num_events)
    ]

    start = time.perf_counter()
    enrich_with_lookup(events_large, users_large)
    lookup_time = time.perf_counter() - start
    print(
        f"Hash map lookup: {lookup_time:.3f}s "
        f"({num_events:,} events, {num_users:,} users)"
    )

    # Only run naive on smaller input to avoid waiting forever
    small_events = events_large[:5_000]
    start = time.perf_counter()
    enrich_naive(small_events, users_large)
    naive_time = time.perf_counter() - start
    projected = naive_time * (num_events / len(small_events))
    print(f"Naive (5K events): {naive_time:.3f}s")
    print(f"Naive projected for {num_events:,} events: ~{projected:.1f}s")
    print(f"Speedup: ~{projected / lookup_time:.0f}x")
