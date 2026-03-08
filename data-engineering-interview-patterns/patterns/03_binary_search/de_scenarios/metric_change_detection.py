"""
DE Scenario: Metric Change Detection

Binary search to find when a metric first crossed a threshold.
Same principle as git bisect.

Usage:
    uv run python -m patterns.03_binary_search.de_scenarios.metric_change_detection
"""

import time


def find_change_linear(
    values: list[float],
    threshold: float,
) -> int | None:
    """
    Linear scan for first index where values[i] > threshold. O(n).

    Assumes values start below threshold and eventually cross it.
    Returns None if threshold is never crossed.
    """
    for i, val in enumerate(values):
        if val > threshold:
            return i
    return None


def find_change_binary(
    values: list[float],
    threshold: float,
) -> int | None:
    """
    Binary search for first index where values[i] > threshold. O(log n).

    Assumes monotonic transition: values start below threshold and
    stay above it once they cross. If this assumption doesn't hold
    (metric bounces), binary search finds one crossing but not
    necessarily the first.
    """
    if not values or values[-1] <= threshold:
        return None

    left, right = 0, len(values) - 1

    while left < right:
        mid = (left + right) // 2
        if values[mid] <= threshold:
            left = mid + 1  # Change hasn't happened yet
        else:
            right = mid  # Change happened at or before mid

    return left


def find_change_with_check(
    dates: list[str],
    check_fn: callable,
) -> int | None:
    """
    Binary search with an expensive check function. O(log n * check_cost).

    This simulates the real-world scenario where you don't have all
    metric values precomputed. Instead, you call check_fn(date) to
    evaluate the metric for a specific date - which might involve
    running a query, building code, or checking a snapshot.

    Returns the index of the first date where check_fn returns True
    (meaning "the problem exists as of this date").
    """
    if not dates:
        return None

    left, right = 0, len(dates) - 1

    while left < right:
        mid = (left + right) // 2
        if not check_fn(dates[mid]):
            left = mid + 1
        else:
            right = mid

    if check_fn(dates[left]):
        return left
    return None


if __name__ == "__main__":
    # Demo: find when error rate crossed 5%
    daily_error_rates = [
        1.2,
        1.5,
        1.3,
        1.8,
        2.0,
        2.1,
        2.3,
        2.5,  # Normal: under 5%
        5.2,
        5.8,
        6.1,
        7.0,
        6.5,
        8.2,
        9.1,  # Elevated: above 5%
    ]
    threshold = 5.0

    idx_linear = find_change_linear(daily_error_rates, threshold)
    idx_binary = find_change_binary(daily_error_rates, threshold)

    print("Demo: Find when error rate first crossed 5%")
    print(f"Daily rates: {daily_error_rates}")
    lin_rate = daily_error_rates[idx_linear]
    bin_rate = daily_error_rates[idx_binary]
    print(f"Linear result: day {idx_linear} (rate={lin_rate:.1f}%)")
    print(f"Binary result: day {idx_binary} (rate={bin_rate:.1f}%)")
    assert idx_linear == idx_binary
    print()

    # Demo: git bisect style with expensive check
    dates = [f"2024-01-{d:02d}" for d in range(1, 32)]
    break_date = "2024-01-18"  # The deploy that broke things

    check_count = 0

    def is_broken(check_date: str) -> bool:
        global check_count
        check_count += 1
        return check_date >= break_date

    result = find_change_with_check(dates, is_broken)
    print(f"Git bisect demo: 31 days, break on {break_date}")
    print(f"Found break at: {dates[result]} (index {result})")
    print(f"Checks performed: {check_count} (vs 31 for linear scan)")
    print("That's ~log2(31) = 5 checks")
    print()

    # Benchmark
    print("--- Benchmark ---")
    for n in [10_000, 100_000, 1_000_000, 10_000_000]:
        # Values that cross threshold at the 60% mark
        crossover = int(n * 0.6)
        values = [float(i < crossover) for i in range(n)]
        # Below threshold = 1.0 (fine), above = 0.0 (broken)
        # Wait, let's make it clearer: values rise past threshold
        values = [i / n * 10 for i in range(n)]  # 0.0 to 10.0
        target = 5.0

        start_time = time.perf_counter()
        result_lin = find_change_linear(values, target)
        linear_time = time.perf_counter() - start_time

        start_time = time.perf_counter()
        result_bin = find_change_binary(values, target)
        binary_time = time.perf_counter() - start_time

        assert result_lin == result_bin
        speedup = linear_time / max(binary_time, 1e-9)
        print(
            f"n={n:>11,} | Change at index {result_bin:>8,} | "
            f"Linear: {linear_time:.5f}s | Binary: {binary_time:.7f}s | "
            f"Speedup: {speedup:,.0f}x"
        )
