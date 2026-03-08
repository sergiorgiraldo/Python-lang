# DE Scenario: Sessionization (Grouping Events into Sessions)

**Run it:** `uv run python -m patterns.04_sliding_window.de_scenarios.sessionization`

## Real-World Context

Web analytics, product analytics and user behavior tracking all need sessionization: grouping a stream of timestamped events into "sessions" based on gaps between events. If a user is active for 5 minutes, goes idle for 45 minutes and comes back, that's two sessions.

The standard approach: sort events by user and timestamp, then scan through looking for gaps that exceed a threshold. When the gap is too large, start a new session.

## The Problem

Given a list of timestamped events for a user, group them into sessions. A new session starts whenever the gap between consecutive events exceeds a timeout threshold.

## Why Sliding Window

This is a variable-size window pattern. The window expands as long as consecutive events are within the timeout. When a gap exceeds the timeout, the current session ends and a new one begins.

It maps to [LeetCode #3 (Longest Substring Without Repeating)](../../problems/003_longest_substring.md) in structure - a variable window that resets when a condition is violated. The "condition" here is the time gap rather than character uniqueness.

## Production Considerations

**Out-of-order events:** In streaming systems, events don't always arrive in order. You need to either sort first (batch) or use watermarks and allowed lateness (streaming) to handle late arrivals that should be part of an earlier session.

**Per-user partitioning:** Sessionization runs independently per user. In SQL this is a window function partitioned by user_id. In Spark or Flink, it's a keyed stream or group-by operation.

**Session ID generation:** Each session needs a unique ID. Common approaches: UUID, hash of (user_id, session_start_time), or a monotonically increasing counter per user.

**SQL approach:** Session detection in SQL typically uses LAG() to compute the gap between events, then a conditional SUM() to assign session numbers:

```sql
SELECT *,
  SUM(CASE WHEN gap_seconds > 1800 THEN 1 ELSE 0 END)
    OVER (PARTITION BY user_id ORDER BY event_time) AS session_id
FROM (
  SELECT *,
    EXTRACT(EPOCH FROM event_time - LAG(event_time)
      OVER (PARTITION BY user_id ORDER BY event_time)) AS gap_seconds
  FROM events
)
```

## Worked Example

Sessionization groups events into sessions based on inactivity gaps. If two consecutive events are more than `gap` minutes apart, they belong to different sessions. This is a variable-size window where the window "breaks" when the gap condition is violated.

```
User click events (sorted by timestamp):
  [10:01, 10:03, 10:07, 10:08, 10:45, 10:47, 10:48, 11:30]

Session gap threshold: 15 minutes

  Event 10:01 → start session 1. Window: [10:01]
  Event 10:03 → gap = 2 min < 15 → same session. Window: [10:01, 10:03]
  Event 10:07 → gap = 4 min → same session. Window grows.
  Event 10:08 → gap = 1 min → same session. Window: [10:01..10:08]

  Event 10:45 → gap = 37 min > 15 → NEW SESSION.
    Close session 1: [10:01, 10:03, 10:07, 10:08] (4 events, 7 min duration)
    Start session 2: [10:45]

  Event 10:47 → gap = 2 min → same session.
  Event 10:48 → gap = 1 min → same session. Window: [10:45..10:48]

  Event 11:30 → gap = 42 min > 15 → NEW SESSION.
    Close session 2: [10:45, 10:47, 10:48] (3 events, 3 min duration)
    Start session 3: [11:30] (1 event)

Result: 3 sessions. Single pass through the sorted events, O(n) time.
This is how Google Analytics and most clickstream tools define sessions.
```

## Connection to LeetCode

Variable window concept from [3. Longest Substring Without Repeating](../../problems/003_longest_substring.md): expand while valid, reset when constraint is violated.

## Benchmark

See the `.py` file for sessionization at scale.
