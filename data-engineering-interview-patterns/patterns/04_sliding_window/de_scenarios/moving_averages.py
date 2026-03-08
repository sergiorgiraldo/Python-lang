"""
DE Scenario: Moving Averages on Time-Series Data

Fixed-size sliding window computing rolling averages.

Usage:
    uv run python -m patterns.04_sliding_window.de_scenarios.moving_averages
"""

import random
import time


def moving_average_naive(values: list[float], k: int) -> list[float]:
    """Recompute sum from scratch for each window. O(n * k)."""
    result = []
    for i in range(len(values) - k + 1):
        result.append(sum(values[i : i + k]) / k)
    return result


def moving_average_sliding(values: list[float], k: int) -> list[float]:
    """Maintain running sum, O(1) per step. O(n) total."""
    if len(values) < k:
        return []

    result = []
    window_sum = sum(values[:k])
    result.append(window_sum / k)

    for i in range(k, len(values)):
        window_sum += values[i] - values[i - k]
        result.append(window_sum / k)

    return result


def moving_average_with_timestamps(
    timestamps: list[float],
    values: list[float],
    window_seconds: float,
) -> list[tuple[float, float]]:
    """
    Time-aware moving average. Window is defined by time, not position.

    Handles gaps in time series correctly. Uses a variable-size window
    that expands and contracts based on actual timestamps.

    Returns list of (timestamp, average) pairs.
    """
    if not timestamps:
        return []

    result = []
    left = 0
    window_sum = 0.0
    count = 0

    for right in range(len(timestamps)):
        window_sum += values[right]
        count += 1

        # Shrink window if time span exceeds window_seconds
        while timestamps[right] - timestamps[left] > window_seconds:
            window_sum -= values[left]
            count -= 1
            left += 1

        result.append((timestamps[right], window_sum / count))

    return result


if __name__ == "__main__":
    # Demo with small dataset
    daily_revenue = [100, 120, 90, 110, 130, 105, 115, 125, 95, 140]
    k = 3

    naive_result = moving_average_naive(daily_revenue, k)
    sliding_result = moving_average_sliding(daily_revenue, k)

    print(f"Daily revenue: {daily_revenue}")
    print(f"3-day moving average (naive):   {[f'{x:.1f}' for x in naive_result]}")
    print(f"3-day moving average (sliding): {[f'{x:.1f}' for x in sliding_result]}")
    print()

    # Verify both agree
    assert len(naive_result) == len(sliding_result)
    for a, b in zip(naive_result, sliding_result):
        assert abs(a - b) < 1e-9
    print("Both approaches agree.\n")

    # Demo time-aware version
    print("--- Time-Aware Moving Average ---")
    # Simulate timestamps with a gap (missing data point)
    timestamps = [0, 1, 2, 3, 4, 7, 8, 9, 10]  # Gap at 5-6
    values = [10, 12, 11, 13, 14, 9, 11, 12, 15]
    result = moving_average_with_timestamps(timestamps, values, 3.0)
    print("Timestamps:", timestamps)
    print("Values:    ", values)
    print("3-second rolling avg:")
    for ts, avg in result:
        print(f"  t={ts}: {avg:.1f}")
    print()

    # Benchmark
    print("--- Benchmark ---")
    random.seed(42)
    for n in [1_000, 10_000, 100_000, 1_000_000]:
        data = [random.uniform(0, 100) for _ in range(n)]
        window = 50

        start_time = time.perf_counter()
        result_naive = moving_average_naive(data, window)
        naive_time = time.perf_counter() - start_time

        start_time = time.perf_counter()
        result_sliding = moving_average_sliding(data, window)
        sliding_time = time.perf_counter() - start_time

        # Verify
        assert len(result_naive) == len(result_sliding)

        speedup = naive_time / max(sliding_time, 1e-9)
        print(
            f"n={n:>10,} k={window:>3} | "
            f"Naive: {naive_time:.4f}s | Sliding: {sliding_time:.4f}s | "
            f"Speedup: {speedup:.0f}x"
        )
