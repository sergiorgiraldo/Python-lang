"""
DE Scenario: Anomaly Detection with Rolling Bounds

Fixed-size sliding window computing rolling mean and std to detect outliers.

Usage:
    uv run python -m patterns.04_sliding_window.de_scenarios.anomaly_detection
"""

import math
import random
import time


def detect_anomalies_naive(
    values: list[float],
    window_size: int,
    threshold: float = 2.0,
) -> list[int]:
    """
    Naive anomaly detection. Recompute mean and std from scratch
    for each window. O(n * k).

    Returns indices of anomalous values.
    """
    anomalies = []
    for i in range(window_size, len(values)):
        window = values[i - window_size : i]
        mean = sum(window) / len(window)
        variance = sum((x - mean) ** 2 for x in window) / len(window)
        std = math.sqrt(variance) if variance > 0 else 0

        if std > 0 and abs(values[i] - mean) > threshold * std:
            anomalies.append(i)

    return anomalies


def detect_anomalies_sliding(
    values: list[float],
    window_size: int,
    threshold: float = 2.0,
) -> list[int]:
    """
    Sliding window anomaly detection. Maintain running sum and
    sum-of-squares for O(1) updates. O(n) total.

    Uses the identity: var = E[x^2] - E[x]^2
    Note: for large values, Welford's algorithm is more stable.

    Returns indices of anomalous values.
    """
    if len(values) <= window_size:
        return []

    anomalies = []

    # Initialize running stats for first window
    window_sum = sum(values[:window_size])
    window_sq_sum = sum(x * x for x in values[:window_size])

    for i in range(window_size, len(values)):
        mean = window_sum / window_size
        variance = (window_sq_sum / window_size) - (mean * mean)
        # Clamp to avoid negative variance from floating point
        std = math.sqrt(max(variance, 0))

        if std > 0 and abs(values[i] - mean) > threshold * std:
            anomalies.append(i)

        # Slide: add values[i], remove values[i - window_size]
        old = values[i - window_size]
        new = values[i]
        window_sum += new - old
        window_sq_sum += new * new - old * old

    return anomalies


if __name__ == "__main__":
    # Demo: inject anomalies into a signal
    random.seed(42)
    n = 100
    # Normal signal with noise
    signal = [50 + random.gauss(0, 5) for _ in range(n)]
    # Inject anomalies
    signal[30] = 100  # Spike
    signal[60] = 10  # Drop
    signal[85] = 95  # Spike

    window = 20
    z_threshold = 2.5

    anomalies_naive = detect_anomalies_naive(signal, window, z_threshold)
    anomalies_sliding = detect_anomalies_sliding(signal, window, z_threshold)

    print("Demo: Anomaly detection on 100-point signal")
    print(f"Window size: {window}, threshold: {z_threshold} std devs")
    print("Injected anomalies at: [30, 60, 85]")
    print(f"Detected (naive):   {anomalies_naive}")
    print(f"Detected (sliding): {anomalies_sliding}")
    assert anomalies_naive == anomalies_sliding
    print("Both approaches agree.\n")

    # Benchmark
    print("--- Benchmark ---")
    for n_points in [10_000, 100_000, 1_000_000]:
        data = [random.gauss(100, 10) for _ in range(n_points)]
        # Inject some anomalies
        for idx in random.sample(range(100, n_points), n_points // 100):
            data[idx] += random.choice([-1, 1]) * 50

        start_time = time.perf_counter()
        result_naive = detect_anomalies_naive(data, 50, 3.0)
        naive_time = time.perf_counter() - start_time

        start_time = time.perf_counter()
        result_sliding = detect_anomalies_sliding(data, 50, 3.0)
        sliding_time = time.perf_counter() - start_time

        assert result_naive == result_sliding
        speedup = naive_time / max(sliding_time, 1e-9)
        print(
            f"n={n_points:>10,} | Anomalies: {len(result_sliding):>5} | "
            f"Naive: {naive_time:.4f}s | Sliding: {sliding_time:.4f}s | "
            f"Speedup: {speedup:.0f}x"
        )
