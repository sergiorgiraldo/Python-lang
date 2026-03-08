# DE Scenario: Rate Limiting with Sliding Windows

**Run it:** `uv run python -m patterns.04_sliding_window.de_scenarios.rate_limiting`

## Real-World Context

API rate limiting, request throttling and abuse detection all need to answer the same question: "how many events happened in the last N seconds?" If the count exceeds a threshold, reject the request or trigger an alert.

Two common approaches:
1. **Fixed windows** (e.g., "max 100 requests per minute") - simple but has boundary spikes. A user could send 100 requests at 0:59 and 100 more at 1:01.
2. **Sliding windows** - count requests in a true rolling window. No boundary artifacts.

## The Problem

Given a stream of request timestamps for a user, determine whether each request should be allowed or rate-limited based on a sliding window policy.

## Why Sliding Window

The fixed window approach (count per calendar minute) is a [643-style](../../problems/643_max_average_subarray.md) fixed window. The sliding window approach is closer to [219 (Contains Duplicate II)](../../problems/219_contains_duplicate_ii.md) - maintaining a set/count of recent items within a distance k.

The key insight: maintain a sorted list (or deque) of recent timestamps. For each new request, remove timestamps that have expired (outside the window), then check if the count exceeds the limit.

## Production Considerations

**Storage backend:** In-memory for single-process rate limiting. Redis sorted sets for distributed systems (ZRANGEBYSCORE to count requests in a time range). Token bucket algorithms are another approach that's simpler to implement but less precise.

**Fixed vs sliding window tradeoff:** Fixed windows are cheaper (one counter per window per user). Sliding windows are more accurate but need to store individual timestamps or use approximation techniques. Some systems use a hybrid: sliding window log for high-value limits, fixed counters for less critical ones.

**Distributed rate limiting:** Multiple application servers checking the same rate limit need shared state. Redis is the standard choice. The algorithm is the same - the timestamp deque just lives in Redis instead of local memory.

**Token bucket alternative:** Instead of counting requests in a window, maintain a "bucket" of tokens that refills at a fixed rate. Each request consumes a token. Simpler to implement but provides different guarantees (burst tolerance vs strict count limits).

## Worked Example

Rate limiting counts events within a sliding time window and rejects new events if the count exceeds a threshold. This is a variable-size window where the "validity" condition is the count staying under the limit.

```
API requests from user_42 (timestamps in seconds):
  [1.0, 1.2, 1.5, 2.0, 2.3, 2.5, 2.8, 3.1, 3.2, 3.5]

Rate limit: max 5 requests per 2-second window

  Request at 1.0: window [1.0]. Count=1 <= 5. ALLOW.
  Request at 1.2: window [1.0, 1.2]. Count=2. ALLOW.
  Request at 1.5: window [1.0, 1.2, 1.5]. Count=3. ALLOW.
  Request at 2.0: window [1.0, 1.2, 1.5, 2.0]. Count=4. ALLOW.
  Request at 2.3: window [1.0, 1.2, 1.5, 2.0, 2.3]. Count=5. ALLOW.

  Request at 2.5: window would be [1.0, 1.2, 1.5, 2.0, 2.3, 2.5].
    But 1.0 is outside the 2-second window (2.5 - 1.0 = 1.5... wait, that's within 2 sec).
    All 6 in window. Count=6 > 5. REJECT.

  Correct: 2-second window ending at 2.5 = [0.5, 2.5].
    All requests from 1.0 to 2.5 are within this range. Count=6 > 5. REJECT.

  Request at 2.8: window [0.8, 2.8].
    Requests in range: [1.0, 1.2, 1.5, 2.0, 2.3, 2.5, 2.8]. Count=7 > 5. REJECT.

  Request at 3.1: window [1.1, 3.1].
    Requests in range: [1.2, 1.5, 2.0, 2.3, 2.5, 2.8, 3.1].
    1.0 is now outside (1.0 < 1.1). Count=7. Still > 5. REJECT.

  Request at 3.2: window [1.2, 3.2].
    Count = 8 (1.2 through 3.2). REJECT.

  Request at 3.5: window [1.5, 3.5].
    Requests: [1.5, 2.0, 2.3, 2.5, 2.8, 3.1, 3.2, 3.5]. Count=8. REJECT.

The burst starting at 2.5 triggered the rate limiter. Earlier requests
gradually age out of the window, allowing new requests eventually.

Implementation: maintain a deque of timestamps. On each request, remove
timestamps older than (current - window_size) from the front. If the
remaining count < limit, allow and append. Otherwise reject.
```

## Connection to LeetCode

Uses the same "maintain recent items within a window" concept as [219. Contains Duplicate II](../../problems/219_contains_duplicate_ii.md). The deque acts as the sliding window of recent timestamps.

## Benchmark

See the `.py` file for rate limiting at scale.
