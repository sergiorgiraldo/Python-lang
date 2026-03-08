"""
DE Scenario: Rate Limiting with Sliding Windows

Sliding window rate limiter vs fixed window rate limiter.

Usage:
    uv run python -m patterns.04_sliding_window.de_scenarios.rate_limiting
"""

import random
import time
from collections import deque


class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter using a deque of timestamps.

    Allows up to `max_requests` in any `window_seconds` period.
    Each request adds a timestamp to the deque. Expired timestamps
    are removed from the front.

    Time: O(1) amortized per request (each timestamp enters and
    exits the deque exactly once).
    Space: O(max_requests) per user.
    """

    def __init__(self, max_requests: int, window_seconds: float):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.timestamps: dict[str, deque[float]] = {}

    def allow_request(self, user_id: str, timestamp: float) -> bool:
        if user_id not in self.timestamps:
            self.timestamps[user_id] = deque()

        dq = self.timestamps[user_id]

        # Remove expired timestamps
        cutoff = timestamp - self.window_seconds
        while dq and dq[0] <= cutoff:
            dq.popleft()

        # Check limit
        if len(dq) < self.max_requests:
            dq.append(timestamp)
            return True
        return False


class FixedWindowRateLimiter:
    """
    Fixed window rate limiter using counters per time bucket.

    Simpler but has boundary artifacts: a burst at the end of one
    window and start of the next can exceed the intended rate.

    Time: O(1) per request
    Space: O(1) per user (just a counter and window ID)
    """

    def __init__(self, max_requests: int, window_seconds: float):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.windows: dict[str, tuple[int, int]] = {}  # user -> (window_id, count)

    def allow_request(self, user_id: str, timestamp: float) -> bool:
        window_id = int(timestamp // self.window_seconds)

        if user_id not in self.windows:
            self.windows[user_id] = (window_id, 0)

        current_window, count = self.windows[user_id]

        if current_window != window_id:
            # New window, reset counter
            self.windows[user_id] = (window_id, 1)
            return True

        if count < self.max_requests:
            self.windows[user_id] = (window_id, count + 1)
            return True

        return False


if __name__ == "__main__":
    # Demo: show the boundary problem with fixed windows
    print("Demo: Fixed vs Sliding Window Rate Limiting")
    print("Policy: max 5 requests per 10 seconds\n")

    fixed = FixedWindowRateLimiter(max_requests=5, window_seconds=10)
    sliding = SlidingWindowRateLimiter(max_requests=5, window_seconds=10)

    # Burst at window boundary: 5 requests at t=9, 5 more at t=11
    requests = [
        ("user_a", 9.0),
        ("user_a", 9.1),
        ("user_a", 9.2),
        ("user_a", 9.3),
        ("user_a", 9.4),
        # Window boundary at t=10
        ("user_a", 10.0),
        ("user_a", 10.1),
        ("user_a", 10.2),
        ("user_a", 10.3),
        ("user_a", 10.4),
    ]

    print(f"{'Time':>6} {'Fixed':>8} {'Sliding':>8}")
    print("-" * 26)
    for user, ts in requests:
        fixed_ok = fixed.allow_request(user, ts)
        sliding_ok = sliding.allow_request(user, ts)
        print(
            f"{ts:>6.1f} {'ALLOW' if fixed_ok else 'DENY':>8} "
            f"{'ALLOW' if sliding_ok else 'DENY':>8}"
        )

    print()
    print("Fixed window allows 10 requests in 2 seconds (boundary exploit).")
    print("Sliding window correctly limits to 5 in any 10-second span.")
    print()

    # Benchmark
    print("--- Benchmark ---")
    random.seed(42)
    for n_requests in [10_000, 100_000, 1_000_000]:
        n_users = 100
        reqs = [
            (f"user_{random.randint(0, n_users - 1)}", random.uniform(0, 3600))
            for _ in range(n_requests)
        ]
        reqs.sort(key=lambda x: x[1])

        sliding_rl = SlidingWindowRateLimiter(max_requests=100, window_seconds=60)
        fixed_rl = FixedWindowRateLimiter(max_requests=100, window_seconds=60)

        start_time = time.perf_counter()
        sliding_allowed = sum(
            1 for user, ts in reqs if sliding_rl.allow_request(user, ts)
        )
        sliding_time = time.perf_counter() - start_time

        start_time = time.perf_counter()
        fixed_allowed = sum(1 for user, ts in reqs if fixed_rl.allow_request(user, ts))
        fixed_time = time.perf_counter() - start_time

        print(
            f"Requests: {n_requests:>10,} | "
            f"Sliding: {sliding_allowed:>7,} allowed ({sliding_time:.3f}s) | "
            f"Fixed: {fixed_allowed:>7,} allowed ({fixed_time:.3f}s)"
        )
