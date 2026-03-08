"""
DE Scenario: Time-Based Log Lookup

Binary search to find log entries within a time window in sorted logs.

Usage:
    uv run python -m patterns.03_binary_search.de_scenarios.log_lookup
"""

import bisect
import random
import time


def find_entries_linear(
    logs: list[dict],
    start_ts: int,
    end_ts: int,
) -> list[dict]:
    """Linear scan for entries in [start_ts, end_ts]. O(n)."""
    return [entry for entry in logs if start_ts <= entry["ts"] <= end_ts]


def find_entries_binary(
    logs: list[dict],
    start_ts: int,
    end_ts: int,
) -> list[dict]:
    """
    Binary search for entries in [start_ts, end_ts]. O(log n + k).

    Find the first entry >= start_ts with bisect, then scan forward
    until we pass end_ts. Total cost is O(log n) for the search
    plus O(k) for reading k matching entries.
    """
    if not logs:
        return []

    # Extract timestamps for bisect (assumes logs are sorted by ts)
    timestamps = [entry["ts"] for entry in logs]

    # Find first entry >= start_ts
    left_idx = bisect.bisect_left(timestamps, start_ts)

    # Scan forward collecting entries until we pass end_ts
    result = []
    for i in range(left_idx, len(logs)):
        if logs[i]["ts"] > end_ts:
            break
        result.append(logs[i])

    return result


def find_entries_binary_no_extract(
    logs: list[dict],
    start_ts: int,
    end_ts: int,
) -> list[dict]:
    """
    Binary search without pre-extracting timestamps. O(log n + k).

    More memory-efficient: doesn't create a separate timestamps list.
    Uses manual binary search since bisect can't directly compare
    dict entries.
    """
    if not logs:
        return []

    # Manual binary search for first entry >= start_ts
    left, right = 0, len(logs)
    while left < right:
        mid = (left + right) // 2
        if logs[mid]["ts"] < start_ts:
            left = mid + 1
        else:
            right = mid

    # Scan forward
    result = []
    for i in range(left, len(logs)):
        if logs[i]["ts"] > end_ts:
            break
        result.append(logs[i])

    return result


if __name__ == "__main__":
    # Demo
    logs = [
        {"ts": 100, "msg": "started"},
        {"ts": 200, "msg": "processed batch 1"},
        {"ts": 300, "msg": "processed batch 2"},
        {"ts": 400, "msg": "checkpoint"},
        {"ts": 500, "msg": "processed batch 3"},
        {"ts": 600, "msg": "completed"},
    ]

    result = find_entries_binary(logs, 200, 400)
    print("Demo: Find log entries between ts=200 and ts=400")
    for entry in result:
        print(f"  ts={entry['ts']}: {entry['msg']}")
    print()

    # Benchmark
    print("--- Benchmark ---")
    random.seed(42)
    n = 1_000_000
    large_logs = [
        {"ts": i * 10 + random.randint(0, 9), "msg": f"event_{i}"} for i in range(n)
    ]
    large_logs.sort(key=lambda x: x["ts"])

    # Query a narrow window in the middle
    mid_ts = large_logs[n // 2]["ts"]
    query_start = mid_ts
    query_end = mid_ts + 1000

    start_time = time.perf_counter()
    result_lin = find_entries_linear(large_logs, query_start, query_end)
    linear_time = time.perf_counter() - start_time

    start_time = time.perf_counter()
    result_bin = find_entries_binary(large_logs, query_start, query_end)
    binary_time = time.perf_counter() - start_time

    start_time = time.perf_counter()
    result_manual = find_entries_binary_no_extract(large_logs, query_start, query_end)
    manual_time = time.perf_counter() - start_time

    assert len(result_lin) == len(result_bin) == len(result_manual)
    print(f"Log entries: {n:,}")
    print(f"Window matches: {len(result_bin)}")
    print(f"Linear scan:            {linear_time:.4f}s")
    print(f"Binary (bisect):        {binary_time:.4f}s")
    print(f"Binary (manual, no extract): {manual_time:.4f}s")
    print()
    print("Note: the bisect version pre-extracts timestamps into a list,")
    print("which adds O(n) memory. The manual version searches the dicts")
    print("directly with O(1) extra memory.")
